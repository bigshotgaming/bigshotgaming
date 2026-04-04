use anyhow::Result;
use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use sqlx::SqlitePool;
use tower_sessions::Session;

use crate::{
    models::User,
};

pub const SESSION_USER_ID_KEY: &str = "user_id";
pub const SESSION_CSRF_KEY: &str = "csrf_token";

/// Hash a plaintext password with Argon2id.
pub fn hash_password(password: &str) -> Result<String> {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();
    let hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| anyhow::anyhow!("Password hashing failed: {e}"))?
        .to_string();
    Ok(hash)
}

/// Verify a plaintext password against a stored hash.
pub fn verify_password(password: &str, hash: &str) -> bool {
    let Ok(parsed) = PasswordHash::new(hash) else {
        return false;
    };
    Argon2::default()
        .verify_password(password.as_bytes(), &parsed)
        .is_ok()
}

/// Retrieve the currently logged-in user from the session, if any.
pub async fn get_current_user(session: &Session, db: &SqlitePool) -> Option<User> {
    let user_id: i64 = session.get(SESSION_USER_ID_KEY).await.ok()??;
    sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
        .bind(user_id)
        .fetch_optional(db)
        .await
        .ok()?
}

/// Generate (or retrieve existing) CSRF token for the session.
pub async fn get_or_create_csrf_token(session: &Session) -> String {
    if let Ok(Some(token)) = session.get::<String>(SESSION_CSRF_KEY).await {
        return token;
    }
    let token = uuid::Uuid::new_v4().to_string();
    let _ = session.insert(SESSION_CSRF_KEY, token.clone()).await;
    token
}

/// Validate a CSRF token from a form POST against the session.
pub async fn validate_csrf(session: &Session, submitted: &str) -> bool {
    let stored: Option<String> = session.get(SESSION_CSRF_KEY).await.unwrap_or(None);
    stored.as_deref() == Some(submitted)
}
