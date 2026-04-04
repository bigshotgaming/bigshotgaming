mod auth;
mod config;
mod error;
mod handlers;
mod models;
mod state;

use std::{net::SocketAddr, path::PathBuf, str::FromStr, sync::Arc};

use axum::{
    routing::{get, post},
    Router,
};
use sqlx::sqlite::{SqliteConnectOptions, SqlitePoolOptions};
use tera::Tera;
use tower_http::services::ServeDir;
use tower_sessions::{MemoryStore, SessionManagerLayer};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

use config::Config;
use handlers::{
    auth_handler::{
        login_get, login_post, logout, password_change_get, password_change_post, register_get,
        register_post,
    },
    carpool::{delete_offer, index as carpool_index, join_offer, leave_offer, new_offer_get,
              new_offer_post, offer_detail},
    events::{
        activate_get, activate_post, index as events_index, participants, payment_get,
        payment_post, register_get as events_register_get, register_post as events_register_post,
    },
    pages::{
        contact_get, contact_post, index as pages_index, post_detail, reviews, sponsors, volunteer_get,
        volunteer_post,
    },
    schedule::index as schedule_index,
    seatmap::{claim_seat, data as seatmap_data, display as seatmap_display},
    tournaments::{
        index as tournaments_index, team_get, team_post, tournament_get, tournament_post,
    },
};
use state::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Load .env if present
    dotenvy::dotenv().ok();

    // Initialise tracing
    tracing_subscriber::registry()
        .with(EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let config = Config::from_env()?;

    // Database
    let opts = SqliteConnectOptions::from_str(&config.database_url)?
        .create_if_missing(true);
    let db = SqlitePoolOptions::new()
        .max_connections(5)
        .connect_with(opts)
        .await?;

    // Run migrations
    let migration_sql = include_str!("../migrations/001_initial.sql");
    for statement in migration_sql.split(';') {
        let stmt = statement.trim();
        if !stmt.is_empty() {
            sqlx::query(stmt).execute(&db).await?;
        }
    }

    // Templates
    let template_glob = "templates/**/*.html";
    let tera = Tera::new(template_glob)?;

    // Session store
    let session_store = MemoryStore::default();
    let session_layer = SessionManagerLayer::new(session_store).with_secure(false);

    let state = AppState {
        db,
        tera: Arc::new(tera),
        config: Arc::new(config.clone()),
    };

    let app = Router::new()
        // Pages
        .route("/", get(pages_index))
        .route("/reviews", get(reviews))
        .route("/post/:id", get(post_detail))
        .route("/contact", get(contact_get).post(contact_post))
        .route("/volunteer", get(volunteer_get).post(volunteer_post))
        .route("/sponsors", get(sponsors))
        // Auth
        .route("/accounts/login", get(login_get).post(login_post))
        .route("/accounts/logout", get(logout))
        .route("/accounts/register", get(register_get).post(register_post))
        .route(
            "/accounts/password/change",
            get(password_change_get).post(password_change_post),
        )
        // Events
        .route("/events", get(events_index))
        .route("/events/register/:id", get(events_register_get).post(events_register_post))
        .route("/events/participants/:id", get(participants))
        .route("/events/payment/:id", get(payment_get).post(payment_post))
        .route(
            "/events/activate/:event_id/:uuid",
            get(activate_get).post(activate_post),
        )
        // Schedule
        .route("/schedule", get(schedule_index))
        // Seatmap
        .route("/seatmap", get(seatmap_display))
        .route("/seatmap/seat/:id/claim", post(claim_seat))
        .route("/seatmap/data/:id", get(seatmap_data))
        // Tournaments
        .route("/tournaments", get(tournaments_index))
        .route(
            "/tournaments/tournament/:id",
            get(tournament_get).post(tournament_post),
        )
        .route("/tournaments/team/:id", get(team_get).post(team_post))
        // Carpool (Issue #16)
        .route("/carpool", get(carpool_index))
        .route("/carpool/offer/new", get(new_offer_get).post(new_offer_post))
        .route("/carpool/offer/:id", get(offer_detail))
        .route("/carpool/offer/:id/join", post(join_offer))
        .route("/carpool/offer/:id/leave", post(leave_offer))
        .route("/carpool/offer/:id/delete", post(delete_offer))
        // Static files
        .nest_service("/static", ServeDir::new("static"))
        .nest_service("/media", ServeDir::new("media"))
        // State & middleware
        .layer(session_layer)
        .with_state(state);

    let addr: SocketAddr = format!("{}:{}", config.host, config.port).parse()?;
    tracing::info!("Listening on http://{addr}");
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    Ok(())
}
