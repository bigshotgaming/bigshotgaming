use std::env;

#[derive(Clone, Debug)]
pub struct Config {
    pub database_url: String,
    pub secret_key: String,
    pub debug: bool,
    pub host: String,
    pub port: u16,
    pub static_url: String,
    pub media_url: String,
    pub media_root: String,
    pub stripe_publishable_key: String,
    pub stripe_secret_key: String,
    pub smtp_host: String,
    pub smtp_port: u16,
    pub smtp_user: String,
    pub smtp_password: String,
    pub from_email: String,
    pub site_name: String,
}

impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        Ok(Self {
            database_url: env::var("DATABASE_URL")
                .unwrap_or_else(|_| "sqlite:bsg.db".to_string()),
            secret_key: env::var("SECRET_KEY")
                .unwrap_or_else(|_| "change-me-in-production".to_string()),
            debug: env::var("DEBUG")
                .map(|v| v == "true" || v == "1")
                .unwrap_or(true),
            host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            port: env::var("PORT")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(8000),
            static_url: env::var("STATIC_URL")
                .unwrap_or_else(|_| "/static/".to_string()),
            media_url: env::var("MEDIA_URL")
                .unwrap_or_else(|_| "/media/".to_string()),
            media_root: env::var("MEDIA_ROOT")
                .unwrap_or_else(|_| "media/".to_string()),
            stripe_publishable_key: env::var("STRIPE_PUBLISHABLE_KEY")
                .unwrap_or_default(),
            stripe_secret_key: env::var("STRIPE_SECRET_KEY")
                .unwrap_or_default(),
            smtp_host: env::var("SMTP_HOST")
                .unwrap_or_else(|_| "localhost".to_string()),
            smtp_port: env::var("SMTP_PORT")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(25),
            smtp_user: env::var("SMTP_USER").unwrap_or_default(),
            smtp_password: env::var("SMTP_PASSWORD").unwrap_or_default(),
            from_email: env::var("FROM_EMAIL")
                .unwrap_or_else(|_| "Big Shot Gaming <bigshot@bigshotgaming.com>".to_string()),
            site_name: env::var("SITE_NAME")
                .unwrap_or_else(|_| "Big Shot Gaming".to_string()),
        })
    }
}
