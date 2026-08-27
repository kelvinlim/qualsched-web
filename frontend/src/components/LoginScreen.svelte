<script lang="ts">
  import * as api from "../lib/api";
  import { errorMessage } from "../lib/types";

  let {
    status,
  }: {
    status: api.AuthStatus;
  } = $props();

  let email = $state("");
  let error = $state("");
  let busy = $state(false);

  async function devSignIn() {
    busy = true;
    error = "";
    try {
      await api.devLogin(email.trim());
      window.location.reload();
    } catch (e) {
      error = errorMessage(e);
    } finally {
      busy = false;
    }
  }
</script>

<div class="login">
  <div class="card">
    <h1>QualSched</h1>
    <p class="subtitle">Researcher sign-in. Participant records stay in Qualtrics.</p>

    {#if error}<div class="banner error">{error}</div>{/if}

    {#if status.google}
      <a class="primary button" href={api.withBase("/auth/login")}>Sign in with Google</a>
      <p class="hint">
        Your Google account must be on the researcher allowlist (SUPERADMIN_EMAILS or an
        existing users row). Google tokens are not stored.
      </p>
    {/if}

    {#if status.devLogin}
      {#if status.google}
        <p class="hint">Or, for local development:</p>
      {:else}
        <p class="hint">
          Google OAuth is not configured. Sign in with an email listed in
          <span class="mono">SUPERADMIN_EMAILS</span>.
        </p>
      {/if}
      <form
        onsubmit={(e) => {
          e.preventDefault();
          void devSignIn();
        }}
      >
        <div class="field">
          <label for="dev-email">Email</label>
          <input
            id="dev-email"
            type="email"
            bind:value={email}
            placeholder="you@umn.edu"
            autocomplete="username"
          />
        </div>
        <button class="primary" type="submit" disabled={busy || !email.trim()}>
          {busy ? "Signing in…" : "Development sign-in"}
        </button>
      </form>
    {/if}

    {#if !status.google && !status.devLogin}
      <div class="banner error">
        No sign-in method is available. Set GOOGLE_CLIENT_ID/SECRET, or run with
        ENVIRONMENT=dev and empty Google client ids.
      </div>
    {/if}
  </div>
</div>

<style>
  .login {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  .login .card {
    width: min(26rem, 100%);
    margin: 0;
  }
  .button {
    display: inline-block;
    text-align: center;
    text-decoration: none;
    padding: 0.5rem 0.85rem;
    border-radius: var(--radius);
    margin-bottom: 0.75rem;
    background: var(--accent);
    border: 1px solid var(--accent);
    color: #fff;
    font-weight: 600;
  }
</style>
