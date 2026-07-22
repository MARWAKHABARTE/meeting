import pytest
from unittest.mock import MagicMock, patch

from app.ai.exceptions import (
    AudioNotFoundException,
    StorageException,
    WhisperException,
    PyannoteException,
    PipelineException
)
from app.ai.storage.audio_loader import AudioLoader
from app.ai.pipeline.transcription_pipeline import TranscriptionPipeline
from app.ai.pipeline.diarization_pipeline import DiarizationPipeline
from app.ai.pipeline.merge_pipeline import MergePipeline
from app.ai.schemas.transcription import TranscriptionResult, TranscriptionSegment
from app.ai.schemas.speaker import DiarizationResult, SpeakerSegment

from app.storage.exceptions import StorageException as SystemStorageException


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tests de Chargement Audio (Audio Loader)
# ──────────────────────────────────────────────────────────────────────────────

def test_audio_loader_file_absent():
    """
    Vérifie que l'AudioLoader lève bien AudioNotFoundException si le fichier n'existe pas.
    """
    loader = AudioLoader()
    # Mock de file_exists qui retourne False
    loader._storage_service.file_exists = MagicMock(return_value=False)
    
    with pytest.raises(AudioNotFoundException):
        with loader.load_audio("bucket", "non_existent.mp3"):
            pass


def test_audio_loader_minio_offline():
    """
    Vérifie que l'AudioLoader propage correctement une StorageException si MinIO est hors ligne.
    """
    loader = AudioLoader()
    # Mock de file_exists qui lève une exception de stockage système
    loader._storage_service.file_exists = MagicMock(side_effect=SystemStorageException("Connexion perdue"))
    
    with pytest.raises(StorageException):
        with loader.load_audio("bucket", "file.mp3"):
            pass


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tests de Modèles IA Hors-ligne / Erreurs de Chargement
# ──────────────────────────────────────────────────────────────────────────────

@patch("app.ai.models.whisper_model.settings")
def test_whisper_offline(mock_settings):
    """
    Vérifie que WhisperException est levée si Whisper échoue à charger ses poids.
    """
    mock_settings.ENVIRONMENT = "production"
    mock_settings.WHISPER_MODEL = "large-v3"
    
    # Simuler l'absence de la lib whisper (ImportError) ou une erreur d'init
    with patch("whisper.load_model", side_effect=Exception("Poids de modèle corrompus")):
        from app.ai.models.whisper_model import WhisperModelProvider
        # Réinitialiser le singleton pour forcer le rechargement
        WhisperModelProvider._instance = None
        with pytest.raises(WhisperException):
            WhisperModelProvider.get_model()


@patch("app.ai.models.pyannote_model.settings")
def test_pyannote_offline(mock_settings):
    """
    Vérifie que PyannoteException est levée en cas d'erreur Hugging Face ou token invalide.
    """
    mock_settings.ENVIRONMENT = "production"
    mock_settings.PYANNOTE_MODEL = "pyannote/speaker-diarization-3.1"
    mock_settings.pyannote_auth_token_to_use = "bad_token"
    
    with patch("pyannote.audio.Pipeline.from_pretrained", side_effect=Exception("Token invalide ou erreur réseau")):
        from app.ai.models.pyannote_model import PyannoteModelProvider
        PyannoteModelProvider._instance = None
        with pytest.raises(PyannoteException):
            PyannoteModelProvider.get_model()


# ──────────────────────────────────────────────────────────────────────────────
# 3. Tests de Validité des Pipelines Individuels
# ──────────────────────────────────────────────────────────────────────────────

def test_transcription_valid():
    """
    Vérifie que la pipeline Whisper retourne un format TranscriptionResult valide.
    """
    pipeline = TranscriptionPipeline()
    # Mock du provider retournant un MockWhisperModel
    from app.ai.models.whisper_model import MockWhisperModel
    pipeline._model_provider.get_model = MagicMock(return_value=MockWhisperModel())
    
    result = pipeline.run("dummy_path.mp3")
    assert isinstance(result, TranscriptionResult)
    assert len(result.segments) > 0
    assert result.segments[0].text == "Bonjour à tous."


def test_diarization_valid():
    """
    Vérifie que la pipeline Pyannote retourne un format DiarizationResult valide.
    """
    pipeline = DiarizationPipeline()
    from app.ai.models.pyannote_model import MockPyannoteModel
    pipeline._model_provider.get_model = MagicMock(return_value=MockPyannoteModel())
    
    result = pipeline.run("dummy_path.mp3")
    assert isinstance(result, DiarizationResult)
    assert len(result.segments) == 3
    assert result.segments[0].speaker == "Speaker 1"


# ──────────────────────────────────────────────────────────────────────────────
# 4. Test d'Alignement Temporel (Fusion)
# ──────────────────────────────────────────────────────────────────────────────

def test_fusion_valid():
    """
    Vérifie que le pipeline de fusion résout correctement le locuteur majoritaire par segment.
    """
    trans = TranscriptionResult(
        text="Bonjour. Bienvenue.",
        language="fr",
        duration=10.0,
        segments=[
            # Segment de 0s à 4s
            TranscriptionSegment(start=0.0, end=4.0, text="Bonjour.", confidence=0.9),
            # Segment de 4s à 10s
            TranscriptionSegment(start=4.0, end=10.0, text="Bienvenue.", confidence=0.8)
        ]
    )
    
    diar = DiarizationResult(
        segments=[
            # Speaker 1 parle principalement au début (de 0s à 3s)
            SpeakerSegment(speaker="Speaker 1", start=0.0, end=3.0, duration=3.0),
            # Speaker 2 parle de 3s à 10s
            SpeakerSegment(speaker="Speaker 2", start=3.0, end=10.0, duration=7.0)
        ]
    )
    
    merge_pipeline = MergePipeline()
    merged = merge_pipeline.run(trans, diar)
    
    assert len(merged.segments) == 2
    # Segment 1 (0-4s) : chevauche Speaker 1 de 0-3s (3s) et Speaker 2 de 3-4s (1s) -> Speaker 1 majoritaire
    assert merged.segments[0].speaker == "Speaker 1"
    # Segment 2 (4-10s) : chevauche uniquement Speaker 2 (6s) -> Speaker 2 majoritaire
    assert merged.segments[1].speaker == "Speaker 2"


# ──────────────────────────────────────────────────────────────────────────────
# 5. Pipeline Complet
# ──────────────────────────────────────────────────────────────────────────────

def test_pipeline_complete():
    """
    Valide l'exécution coordonnée de toutes les étapes sur des modèles bouchonnés.
    """
    t_pipeline = TranscriptionPipeline()
    d_pipeline = DiarizationPipeline()
    m_pipeline = MergePipeline()
    
    from app.ai.models.whisper_model import MockWhisperModel
    from app.ai.models.pyannote_model import MockPyannoteModel
    
    t_pipeline._model_provider.get_model = MagicMock(return_value=MockWhisperModel())
    d_pipeline._model_provider.get_model = MagicMock(return_value=MockPyannoteModel())
    
    trans_res = t_pipeline.run("dummy.mp3")
    diar_res = d_pipeline.run("dummy.mp3")
    pipeline_result = m_pipeline.run(trans_res, diar_res)
    
    assert pipeline_result.full_text != ""
    assert len(pipeline_result.segments) == 3
    assert pipeline_result.segments[0].speaker == "Speaker 1"
    assert pipeline_result.segments[1].speaker == "Speaker 2"
