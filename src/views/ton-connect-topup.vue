<template>
    <div class="ton-connect-container">
      <div id="ton-connect"></div>
    </div>
  </template>
  
  <script>
  import { onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { TonConnectUI } from '@tonconnect/ui'
  
  export default {
    setup() {
      const router = useRouter()
  
      const processTransaction = async (tonConnectUI) => {
        const amount = localStorage.getItem('topUpAmount') || '100000000'
        
        const transaction = {
          validUntil: Math.floor(Date.now() / 1000) + 300,
          messages: [{
            address: "UQCm6we41JB5_a-bz581Yarp2WUc7btjWozHr-j9UaRgO_Sf",
            amount: amount
          }]
        }
  
        try {
          const result = await tonConnectUI.sendTransaction(transaction)
          console.log('Transaction successful:', result)
          alert(`Успешно отправлено ${amount / 1000000000} TON!`)
          router.back()
        } catch (error) {
          if (error.message !== 'User rejects transaction') {
            alert(`Ошибка транзакции: ${error.message}`)
          }
          router.back()
        }
      }
  
      onMounted(() => {
        const tonConnectUI = new TonConnectUI({
          manifestUrl: 'https://raw.githubusercontent.com/SivchSP/Manifest/main/tonconnect-manifest.json',
          buttonRootId: 'ton-connect'
        })
  
        tonConnectUI.onStatusChange((wallet) => {
          if (wallet) {
            processTransaction(tonConnectUI)
          }
        })
      })
  
      return {}
    }
  }
  </script>