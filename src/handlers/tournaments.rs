use axum::{
    extract::{Form, Path, State},
    response::{IntoResponse, Redirect, Response},
};
use serde::Deserialize;
use tower_sessions::Session;

use crate::{
    auth::{get_current_user, get_or_create_csrf_token, validate_csrf},
    error::{render, AppError},
    models::{Event, MemberRow, Participant, Team, TeamListRow, Tournament, TournamentListRow},
    state::AppState,
};
use crate::handlers::pages::build_base_ctx;

// ── Tournament Index ──────────────────────────────────────────────────────────

pub async fn index(
    State(state): State<AppState>,
    session: Session,
) -> Result<impl IntoResponse, AppError> {
    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE is_active = 1 LIMIT 1")
        .fetch_optional(&state.db)
        .await?;

    let tournaments: Vec<TournamentListRow> = if let Some(ref e) = event {
        sqlx::query_as::<_, TournamentListRow>(r#"
            SELECT t.id, t.name, t.max_teams,
                   CAST(COALESCE((SELECT COUNT(*) FROM teams WHERE tournament_id = t.id), 0) AS INTEGER) as "team_count: i64"
              FROM tournaments t
             WHERE t.event_id = ? AND t.is_active = 1
             ORDER BY t.name
            "#)
        .bind(e.id)
        .fetch_all(&state.db)
        .await?
    } else {
        Vec::new()
    };

    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("event", &event);
    ctx.insert("tournaments", &tournaments);
    render(&state.tera, "tournaments/index.html", &ctx)
}

// ── Tournament Detail ─────────────────────────────────────────────────────────

pub async fn tournament_get(
    State(state): State<AppState>,
    session: Session,
    Path(pk): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let tournament = sqlx::query_as::<_, Tournament>("SELECT * FROM tournaments WHERE id = ?")
        .bind(pk)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(tournament.event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let teams = sqlx::query_as::<_, TeamListRow>(r#"
        SELECT t.id, t.name, t.tournament_id, t.owner_id,
               CAST(COALESCE((SELECT COUNT(*) FROM team_members WHERE team_id = t.id), 0) AS INTEGER) as "member_count: i64",
               u.username as owner_username
          FROM teams t
          JOIN participants p ON p.id = t.owner_id
          JOIN users u ON u.id = p.user_id
         WHERE t.tournament_id = ?
         ORDER BY t.name
        "#)
        .bind(pk)
    .fetch_all(&state.db)
    .await?;

    let user = get_current_user(&session, &state.db).await;
    let participant: Option<Participant> = if let Some(u) = &user {
        sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(u.id)
        .bind(tournament.event_id)
        .fetch_optional(&state.db)
        .await?
    } else {
        None
    };

    let has_coupon: bool = if let Some(ref p) = participant {
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM coupons WHERE participant_id = ? AND activated = 1")
        .bind(p.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0)
            > 0
    } else {
        false
    };

    let style_display = tournament.style_display();
    let team_count = teams.len();

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("tournament", &tournament);
    ctx.insert("style_display", style_display);
    ctx.insert("event", &event);
    ctx.insert("teams", &teams);
    ctx.insert("team_count", &team_count);
    ctx.insert("participant", &participant);
    ctx.insert("has_coupon", &has_coupon);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "tournaments/tournament.html", &ctx)
}

#[derive(Deserialize)]
pub struct CreateTeamForm {
    pub name: String,
    pub password: String,
    pub csrf_token: String,
}

pub async fn tournament_post(
    State(state): State<AppState>,
    session: Session,
    Path(pk): Path<i64>,
    Form(form): Form<CreateTeamForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let tournament = sqlx::query_as::<_, Tournament>("SELECT * FROM tournaments WHERE id = ?")
        .bind(pk)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let team_count: i64 =
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM teams WHERE tournament_id = ?")
        .bind(pk)
            .fetch_one(&state.db)
            .await.unwrap_or(0) as i64;
    if team_count >= tournament.max_teams {
        return Err(AppError::BadRequest("This tournament is full.".into()));
    }

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(tournament.event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::BadRequest(
        "You must be registered for this event to create a team.".into(),
    ))?;

    // Remove from any existing team in this tournament
    let existing_team_id: Option<i64> = sqlx::query_scalar::<_, i64>("SELECT tm.team_id FROM team_members tm JOIN teams t ON t.id = tm.team_id WHERE tm.participant_id = ? AND t.tournament_id = ?")
        .bind(participant.id)
        .bind(pk)
    .fetch_optional(&state.db)
    .await?;

    if let Some(tid) = existing_team_id {
        sqlx::query!(
            "DELETE FROM team_members WHERE team_id = ? AND participant_id = ?",
            tid,
            participant.id
        )
        .execute(&state.db)
        .await?;
    }

    let new_team_id: i64 = sqlx::query!(
        "INSERT INTO teams (name, password, tournament_id, owner_id) VALUES (?, ?, ?, ?) RETURNING id",
        form.name,
        form.password,
        pk,
        participant.id
    )
    .fetch_one(&state.db)
    .await?
    .id;

    sqlx::query!(
        "INSERT INTO team_members (team_id, participant_id) VALUES (?, ?)",
        new_team_id,
        participant.id
    )
    .execute(&state.db)
    .await?;

    Ok(Redirect::to(&format!("/tournaments/tournament/{pk}")).into_response())
}

// ── Team Detail ───────────────────────────────────────────────────────────────

pub async fn team_get(
    State(state): State<AppState>,
    session: Session,
    Path(pk): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    let team = sqlx::query_as::<_, Team>("SELECT * FROM teams WHERE id = ?")
        .bind(pk)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let tournament = sqlx::query_as::<_, Tournament>("SELECT * FROM tournaments WHERE id = ?")
        .bind(team.tournament_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let event = sqlx::query_as::<_, Event>("SELECT * FROM events WHERE id = ?")
        .bind(tournament.event_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let members = sqlx::query_as::<_, MemberRow>(r#"
        SELECT u.username
          FROM team_members tm
          JOIN participants p ON p.id = tm.participant_id
          JOIN users u ON u.id = p.user_id
         WHERE tm.team_id = ?
        "#)
        .bind(pk)
    .fetch_all(&state.db)
    .await?;

    let owner_username: String = sqlx::query_scalar::<_, String>("SELECT u.username FROM participants p JOIN users u ON u.id = p.user_id WHERE p.id = ?")
        .bind(team.owner_id)
    .fetch_one(&state.db)
    .await
        .unwrap_or_default();

    let user = get_current_user(&session, &state.db).await;
    let participant: Option<Participant> = if let Some(u) = &user {
        sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(u.id)
        .bind(tournament.event_id)
        .fetch_optional(&state.db)
        .await?
    } else {
        None
    };

    let on_team: bool = if let Some(ref p) = participant {
        sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM team_members WHERE team_id = ? AND participant_id = ?")
        .bind(pk)
        .bind(p.id)
        .fetch_one(&state.db)
        .await
        .unwrap_or(0)
            > 0
    } else {
        false
    };

    let team_full = (members.len() as i64) >= tournament.team_size;

    let csrf = get_or_create_csrf_token(&session).await;
    let mut ctx = build_base_ctx(&state, &session).await;
    ctx.insert("team", &team);
    ctx.insert("tournament", &tournament);
    ctx.insert("event", &event);
    ctx.insert("members", &members);
    ctx.insert("owner_username", &owner_username);
    ctx.insert("participant", &participant);
    ctx.insert("on_team", &on_team);
    ctx.insert("team_full", &team_full);
    ctx.insert("csrf_token", &csrf);
    ctx.insert("errors", &Vec::<String>::new());
    render(&state.tera, "tournaments/team.html", &ctx)
}

#[derive(Deserialize)]
pub struct TeamActionForm {
    pub action: Option<String>,
    pub password: Option<String>,
    pub csrf_token: String,
}

pub async fn team_post(
    State(state): State<AppState>,
    session: Session,
    Path(pk): Path<i64>,
    Form(form): Form<TeamActionForm>,
) -> Result<Response, AppError> {
    if !validate_csrf(&session, &form.csrf_token).await {
        return Err(AppError::BadRequest("Invalid CSRF token.".into()));
    }

    let user = get_current_user(&session, &state.db)
        .await
        .ok_or(AppError::Unauthorized)?;

    let team = sqlx::query_as::<_, Team>("SELECT * FROM teams WHERE id = ?")
        .bind(pk)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let tournament = sqlx::query_as::<_, Tournament>("SELECT * FROM tournaments WHERE id = ?")
        .bind(team.tournament_id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(AppError::NotFound)?;

    let participant = sqlx::query_as::<_, Participant>("SELECT * FROM participants WHERE user_id = ? AND event_id = ?")
        .bind(user.id)
        .bind(tournament.event_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::BadRequest("You must be registered for this event.".into()))?;

    let action = form.action.as_deref().unwrap_or("join");

    match action {
        "join" => {
            let member_count: i64 =
                sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM team_members WHERE team_id = ?")
        .bind(pk)
                    .fetch_one(&state.db)
                    .await.unwrap_or(0) as i64;
            if member_count >= tournament.team_size {
                return Err(AppError::BadRequest("This team is full.".into()));
            }
            if form.password.as_deref() != Some(&team.password) {
                return Err(AppError::BadRequest("Incorrect team password.".into()));
            }
            sqlx::query!(
                "INSERT OR IGNORE INTO team_members (team_id, participant_id) VALUES (?, ?)",
                pk,
                participant.id
            )
            .execute(&state.db)
            .await?;
        }
        "leave" => {
            sqlx::query!(
                "DELETE FROM team_members WHERE team_id = ? AND participant_id = ?",
                pk,
                participant.id
            )
            .execute(&state.db)
            .await?;

            let remaining: i64 =
                sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM team_members WHERE team_id = ?")
        .bind(pk)
                    .fetch_one(&state.db)
                    .await.unwrap_or(0) as i64;
            if remaining == 0 {
                sqlx::query!("DELETE FROM teams WHERE id = ?", pk)
                    .execute(&state.db)
                    .await?;
                return Ok(
                    Redirect::to(&format!("/tournaments/tournament/{}", team.tournament_id))
                        .into_response(),
                );
            }
            if team.owner_id == participant.id {
                let new_owner: i64 = sqlx::query_scalar::<_, i64>("SELECT participant_id FROM team_members WHERE team_id = ? LIMIT 1")
        .bind(pk)
                .fetch_one(&state.db)
                .await
        .unwrap_or(0);
                sqlx::query!(
                    "UPDATE teams SET owner_id = ? WHERE id = ?",
                    new_owner,
                    pk
                )
                .execute(&state.db)
                .await?;
            }
        }
        "delete" if team.owner_id == participant.id => {
            sqlx::query!("DELETE FROM team_members WHERE team_id = ?", pk)
                .execute(&state.db)
                .await?;
            sqlx::query!("DELETE FROM teams WHERE id = ?", pk)
                .execute(&state.db)
                .await?;
            return Ok(
                Redirect::to(&format!("/tournaments/tournament/{}", team.tournament_id))
                    .into_response(),
            );
        }
        _ => return Err(AppError::BadRequest("Unknown action.".into())),
    }

    Ok(Redirect::to(&format!("/tournaments/team/{pk}")).into_response())
}

