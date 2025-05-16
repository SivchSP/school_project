<template>
    <div class="ton-connect-container">
      <h1>TonConnect Integration</h1>
      <div id="connect-button"></div>
      
      <div v-if="connected" class="wallet-info">
        <h2>Wallet Information</h2>
        <p><strong>Address:</strong> {{ walletAddress }}</p>
        <p><strong>Chain:</strong> {{ walletChain }}</p>
        <button @click="disconnect" class="disconnect-btn">Disconnect Wallet</button>
      </div>
    </div>
  </template>
  
  <script>
  import { onMounted, ref } from 'vue';
  import { TonConnectUI } from '@tonconnect/ui';
  
  export default {
    name: 'TonConnectPage',
    setup() {
      const tonConnectUI = ref(null);
      const connected = ref(false);
      const walletAddress = ref('');
      const walletChain = ref('');
  
      onMounted(() => {
        // Инициализация TonConnectUI
        tonConnectUI.value = new TonConnectUI({
          manifestUrl: 'https://your-app-url.com/tonconnect-manifest.json',
          buttonRootId: 'connect-button'
        });
  
        // Проверка существующего соединения
        tonConnectUI.value.connectionRestored.then(() => {
          const walletConnectionSource = tonConnectUI.value.wallet;
          if (walletConnectionSource) {
            updateWalletInfo(walletConnectionSource);
          }
        });
  
        // Подписка на изменения кошелька
        tonConnectUI.value.onStatusChange((wallet) => {
          if (wallet) {
            updateWalletInfo(wallet);
          } else {
            resetWalletInfo();
          }
        });
      });
  
      const updateWalletInfo = (wallet) => {
        connected.value = true;
        walletAddress.value = wallet.account.address;
        walletChain.value = wallet.account.chain;
      };
  
      const resetWalletInfo = () => {
        connected.value = false;
        walletAddress.value = '';
        walletChain.value = '';
      };
  
      const disconnect = async () => {
        await tonConnectUI.value.disconnect();
        resetWalletInfo();
      };
  
      return {
        connected,
        walletAddress,
        walletChain,
        disconnect
      };
    }
  };
  </script>
  
  <style scoped>
  .ton-connect-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
  }
  
  .wallet-info {
    margin-top: 20px;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 8px;
  }
  
  .disconnect-btn {
    margin-top: 10px;
    padding: 8px 16px;
    background-color: #ff4444;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .disconnect-btn:hover {
    background-color: #cc0000;
  }
  </style>