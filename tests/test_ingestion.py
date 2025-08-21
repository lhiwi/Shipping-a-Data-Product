from src.utils.config import TelegramConfig

def test_telegram_config_defaults():
    cfg = TelegramConfig()
    assert isinstance(cfg.api_id, int)
    assert isinstance(cfg.api_hash, str)
    assert len(cfg.channels) >= 1
