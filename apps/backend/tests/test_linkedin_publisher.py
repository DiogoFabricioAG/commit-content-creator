from app.config import Settings
from app.linkedin.publisher import LinkedInPublisher
from app.linkedin.security import decrypt_token, encrypt_token


def test_token_encryption_and_decryption() -> None:
    raw_token = "AQV987654321_secret_linkedin_oauth_token"
    enc = encrypt_token(raw_token)
    assert enc != raw_token
    dec = decrypt_token(enc)
    assert dec == raw_token


def test_linkedin_publisher_demo_mode() -> None:
    settings = Settings(app_env="test", demo_mode=True)
    publisher = LinkedInPublisher(settings)

    res = publisher.publish_post(
        author_urn="urn:li:person:mock_dev",
        commentary="Testing Proof of Work automated publishing.",
    )

    assert res.status == "published"
    assert res.post_urn.startswith("urn:li:share:pow_demo_")
