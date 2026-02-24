/**
 * CSV エクスポート/インポート機能
 */

(function() {
  'use strict';

  // エクスポートボタンの処理
  const exportBtn = document.getElementById('exportCsv');
  if (exportBtn) {
    exportBtn.addEventListener('click', async function() {
      try {
        const response = await fetch('/api/export/csv');
        if (!response.ok) {
          throw new Error('エクスポートに失敗しました');
        }
        
        // Blobとしてダウンロード
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pomodoro_data_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // 成功メッセージを表示
        showNotification('CSVエクスポートが完了しました', 'success');
      } catch (error) {
        console.error('Export error:', error);
        showNotification('エクスポートに失敗しました', 'error');
      }
    });
  }

  // インポートボタンの処理
  const importInput = document.getElementById('importCsv');
  if (importInput) {
    importInput.addEventListener('change', async function(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // ファイル拡張子チェック
      if (!file.name.endsWith('.csv')) {
        showNotification('CSVファイルを選択してください', 'error');
        event.target.value = '';
        return;
      }
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/import/csv', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'インポートに失敗しました');
        }
        
        // 成功メッセージを表示
        showNotification(data.message || `${data.imported_count}件のデータをインポートしました`, 'success');
        
        // 統計情報を更新
        if (window.updateStats) {
          window.updateStats();
        }
        if (window.GamificationUI && window.GamificationUI.updateDisplay) {
          window.GamificationUI.updateDisplay();
        }
      } catch (error) {
        console.error('Import error:', error);
        showNotification(error.message || 'インポートに失敗しました', 'error');
      } finally {
        // ファイル入力をリセット
        event.target.value = '';
      }
    });
  }

  /**
   * 通知を表示
   */
  function showNotification(message, type = 'info') {
    // 既存の通知コンテナを探す、なければ作成
    let container = document.getElementById('notificationContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'notificationContainer';
      container.className = 'notification-container';
      document.body.appendChild(container);
    }
    
    // 通知要素を作成
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // アニメーション
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    // 3秒後に削除
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        container.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // グローバルに公開（他のスクリプトから使えるように）
  window.CSVManager = {
    showNotification
  };
})();
