/**
 * 認証UI管理
 */

(function() {
  'use strict';

  // DOMContentLoadedで初期化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    loadCurrentUser();
    setupLogoutButton();
  }

  /**
   * 現在のログインユーザー情報を読み込む
   */
  async function loadCurrentUser() {
    try {
      const response = await fetch('/auth/current-user');
      if (!response.ok) {
        return;
      }

      const data = await response.json();
      
      if (data.authenticated) {
        // ユーザー名を表示
        const userElement = document.getElementById('currentUser');
        if (userElement) {
          userElement.textContent = `(${data.username})`;
        }

        // ログアウトボタンを表示
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
          logoutBtn.style.display = 'block';
        }
      }
    } catch (error) {
      console.error('Failed to load current user:', error);
    }
  }

  /**
   * ログアウトボタンのセットアップ
   */
  function setupLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', async () => {
      if (!confirm('ログアウトしますか？')) {
        return;
      }

      try {
        const response = await fetch('/auth/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({})
        });

        if (response.ok) {
          // ログインページにリダイレクト
          window.location.href = '/auth/login';
        }
      } catch (error) {
        console.error('Logout failed:', error);
        alert('ログアウトに失敗しました');
      }
    });
  }

  // グローバルに公開
  window.AuthUI = {
    loadCurrentUser
  };
})();
