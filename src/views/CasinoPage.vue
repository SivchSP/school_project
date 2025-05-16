<template>
    <div class="casino-page">
     <div class="page">
      <h1>АМАХАСЛА</h1>
      <div class="balance-info">
        <p>Баланс: {{ formatNumber(currentScore) }}</p>
     </div>
        <div class="nft-counts">
        <div v-for="nft in nfts" :key="nft.id" class="nft-count">
          <img :src="getNftImage(nft.id)" :alt="'NFT ' + nft.id">
          <span>x{{ userNfts[nft.id] || 0 }}</span>
        </div>
      </div>
      </div>
  
      <div class="roulette-container">
        <div class="roulette-wheel" :style="{ transform: `translateX(${wheelPosition}px)` }">
          <div 
            v-for="(item, index) in [...wheelItems, ...wheelItems, ...wheelItems]" 
            :key="index" 
            class="wheel-item"
            :class="getItemClass(item)"
          >
            <img v-if="item.type === 'nft'" :src="getNftImage(item.id)" alt="NFT">
            <span v-else>{{ item.value }}</span>
          </div>
        </div>
        <div class="center-line"></div>
      </div>
  
      <button 
        class="spin-button" 
        @click="spinWheel" 
        :disabled="isSpinning || !canSpin"
      >
        {{ spinButtonText }}
      </button>
  
  
      <div v-if="lastWin" class="win-message">
        <p>Вы выиграли: {{ lastWin.type === 'nft' ? 'NFT ' + lastWin.id : formatNumber(lastWin.value) + ' AMHSL' }}!</p>
      </div>
    </div>
  </template>
  
  <script>
  import { createClient } from '@supabase/supabase-js'
  import  nft1  from '@/assets/nft1.png'
  import  nft2  from '@/assets/nft2.png'
  import  nft5  from '@/assets/nft5.png'
  import  nft4  from '@/assets/nft4.png'
  import  nft3  from '@/assets/nft3.png'
  import  nft6  from '@/assets/nft6.png'
  import  nft7  from '@/assets/nft7.png'
  import  nft8  from '@/assets/nft8.png'
  import  nft9  from '@/assets/nft9.png'
  import  nft10  from '@/assets/nft10.png'
  const supabaseUrl = 'https://jgkfvqiophgvswqvatbx.supabase.co'
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impna2Z2cWlvcGhndnN3cXZhdGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk4ODI5NTMsImV4cCI6MjA1NTQ1ODk1M30.GTN1V9NJwnmwy8GmXOOz3SxepV7n4yVKkhLYZTYuFEQ'
  const supabase = createClient(supabaseUrl, supabaseKey)
  
  export default {
    name: 'CasinoPage',
    data() {
      return {
        currentScore: 0,
        currentUserName: '',
        userNfts: {
          1: 0,
          // 2: 0,
          // 3: 0,
          // 4: 0,
          // 5: 0,
          // 6: 0,
          // 7: 0,
          // 8: 0,
          // 9: 0,
          // 10: 0
        },
        spinsAvailable: 0,
        isSpinning: false,
        wheelPosition: 0,
        lastWin: null,
        wheelItems: [
          { type: 'coin', value: 10000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 20000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 30000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 60000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 15000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 25000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 30000 },
          { type: 'coin', value: 20000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 25000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 10000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 15000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 30000 },
          { type: 'coin', value: 15000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 10000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 15000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 30000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 5000 },
          { type: 'nft', id: 1 },
          { type: 'coin', value: 10000 }
        ],
        nfts: [
          { id: 1, name: 'NFT 1' },
          // { id: 2, name: 'NFT 2' },
          // { id: 3, name: 'NFT 3' },
          // { id: 4, name: 'NFT 4' },
          // { id: 5, name: 'NFT 5' },
          // { id: 6, name: 'NFT 6' },
          // { id: 7, name: 'NFT 7' },
          // { id: 8, name: 'NFT 8' },
          // { id: 9, name: 'NFT 9' },
          // { id: 10, name: 'NFT 10' }
        ],
        nftImages: {
          1: nft1,
          // 2: nft2,
          // 3: nft3,
          // 4: nft4,
          // 5: nft5,
          // 6: nft6,
          // 7: nft7,
          // 8: nft8,
          // 9: nft9,
          // 10: nft10
        },
        spinCost: 20000,
        animationFrameId: null,
        winItem: null,
        isShowingWin: false
      }
    },
    computed: {
      canSpin() {
        return this.currentScore >= this.spinCost || this.spinsAvailable > 0
      },
      spinButtonText() {
        if (this.isSpinning || this.isShowingWin) return 'Крутится...'
        if (this.spinsAvailable > 0) return 'Крутить рулетку (бесплатно)'
        return `Крутить рулетку (${this.formatNumber(this.spinCost)})`
      }
    },
    async created() {
      await this.fetchUserData()
    },
    beforeUnmount() {
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId)
      }
    },
    methods: {
      async fetchUserData() {
        try {
          const savedAccount = localStorage.getItem('currentAccount')
          if (!savedAccount) return
  
          const account = JSON.parse(savedAccount)
          this.currentUserName = account.name
  
          const { data: userData, error } = await supabase
            .from('users')
            .select('*')
            .eq('name', this.currentUserName)
            .single()
            if (error) throw error
        this.currentScore = userData.score || 0
        this.userNfts = {
          1: userData['nft1'] || 0,
          // 2: userData['nft2'] || 0,
          // 3: userData['nft3'] || 0,
          // 4: userData['nft4'] || 0,
          // 5: userData['nft5'] || 0,
          // 6: userData['nft6'] || 0,
          // 7: userData['nft7'] || 0,
          // 8: userData['nft8'] || 0,
          // 9: userData['nft9'] || 0,
          // 10: userData['nft10'] || 0
        }
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error)
      }
    },

    spinWheel() {
      if (this.isSpinning || this.isShowingWin) return
      
      if (this.spinsAvailable <= 0 && this.currentScore < this.spinCost) {
        alert('Недостаточно мемкоинов для прокрутки рулетки!')
        return
      }
      
      this.isSpinning = true
      this.lastWin = null
      this.isShowingWin = false

      const winIndex = Math.floor(Math.random() * this.wheelItems.length)
      this.winItem = this.wheelItems[winIndex]
      
      const spinDuration = 20000
      const slowDownDuration = 6000
      const startTime = performance.now()
      const startPosition = this.wheelPosition
      const itemWidth = 100
      const spinsCount = 1
      
      const targetPosition = -((winIndex + this.wheelItems.length * 2) * itemWidth + itemWidth / 2)
      
      const totalDistance = spinsCount * this.wheelItems.length * itemWidth + 
                          Math.abs(targetPosition - (startPosition % (this.wheelItems.length * itemWidth)))

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / spinDuration, 1)
        
        const easing = Math.sin(progress * Math.PI / 2)
        
        this.wheelPosition = startPosition - totalDistance * easing
        
        const maxOffset = this.wheelItems.length * itemWidth
        if (Math.abs(this.wheelPosition) > maxOffset * 3) {
          this.wheelPosition += this.wheelPosition > 0 ? -maxOffset : maxOffset
        }
        
        if (progress < 1) {
          this.animationFrameId = requestAnimationFrame(animate)
        } else {
          this.wheelPosition = -((winIndex % this.wheelItems.length) * itemWidth + itemWidth / 2)
          this.isSpinning = false
          this.isShowingWin = true
          
          setTimeout(() => {
            this.finishSpin(this.winItem)
            this.isShowingWin = false
          }, 2000)
        }
      }
      
      this.animationFrameId = requestAnimationFrame(animate)
      
      if (this.spinsAvailable <= 0) {
        this.updateScore(-this.spinCost)
      } else {
        this.spinsAvailable--
      }
    },

    async finishSpin(winItem) {
      try {
        this.lastWin = winItem
        
        if (winItem.type === 'nft') {
          const nftId = winItem.id
          this.userNfts[nftId] = (this.userNfts[nftId] || 0) + 1
          
          await this.updateNftCount(nftId, this.userNfts[nftId])
        } else {
          await this.updateScore(winItem.value)
        }
      } catch (error) {
        console.error('Ошибка при обработке выигрыша:', error)
        if (winItem.type === 'nft') {
          this.userNfts[winItem.id] = Math.max(0, this.userNfts[winItem.id] - 1)
        }
      }
    },
    
    async updateNftCount(nftId, newCount) {
      try {
        if (!this.currentUserName) {
          throw new Error('Имя пользователя не определено')
        }

        const columnName = `nft${nftId}`
        
        const { data: currentData, error: fetchError } = await supabase
          .from('users')
          .select(columnName)
          .eq('name', this.currentUserName)
          .single()

        if (fetchError) throw fetchError

        const { error: updateError } = await supabase
          .from('users')
          .update({ [columnName]: newCount })
          .eq('name', this.currentUserName)

        if (updateError) throw updateError

        this.updateLocalStorageAccount(null, nftId)
      } catch (error) {
        console.error(`Ошибка при обновлении NFT ${nftId}:, error`)
        throw error
      }
    },

    async updateScore(amount) {
      try {
        if (!this.currentUserName) return
        const newScore = Math.max(0, this.currentScore + amount)
        
        const { error } = await supabase
          .from('users')
          .update({ score: newScore })
          .eq('name', this.currentUserName)

        if (error) throw error

        this.currentScore = newScore
        this.updateLocalStorageAccount(newScore)
      } catch (error) {
        console.error('Ошибка при обновлении счета:', error)
        throw error
      }
    },

    updateLocalStorageAccount(newScore = null, nftId = null) {
      try {
        const savedAccount = localStorage.getItem('currentAccount')
        if (!savedAccount) return

        const account = JSON.parse(savedAccount)

        if (newScore !== null) {
          account.score = newScore
        }

        if (nftId !== null) {
          account[`nft${nftId}`] = this.userNfts[nftId]
        }

        localStorage.setItem('currentAccount', JSON.stringify(account))
      } catch (error) {
        console.error('Ошибка при обновлении localStorage:', error)
      }
    },

    getItemClass(item) {
      return {
        'coin-item': item.type === 'coin',
        'nft-item': item.type === 'nft',
        [`nft${item.id}`]: item.type === 'nft'
      }
    },

    getNftImage(id) {
      return this.nftImages[id]
    },

    formatNumber(num) {
      return new Intl.NumberFormat('ru-RU').format(num)
    }
  }
}
</script>
<style scoped>
.page {
  max-width: 340px;
  max-height: 270px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  font-family: Arial, sans-serif;
  background-color: #ffd000;
  border-radius: 15px;

}
.casino-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  font-family: Arial, sans-serif;
  background-color: #1d1d1d;
  border-radius: 15px;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.3);


}

.balance-info {
  margin: 20px 0;
  font-size: 18px;
}

.balance-info p {
  margin: 5px 0;
}

.roulette-container {
  position: relative;
  width: 100%;
  height: 120px;
  margin: 40px 0;
  overflow: hidden;
  border: 2px solid #333;
  border-radius: 10px;
  background-color: #f5f5f5;
}

.roulette-wheel {
  display: flex;
  position: absolute;
  height: 100%;
  will-change: transform;
  left: 50%;
  transition: transform 0.s linear;
}

.wheel-item {
  width: 100px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px dashed #ccc;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.coin-item {
  background-color: #ffd900;
  color: #333;
}

.nft-item {
  background-color: #ffffff;
  color: white;
}

.nft-item img {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.center-line {
  position: absolute;
  top: 0;
  left: 50%;
  width: 3px;
  height: 100%;
  background-color: rgb(255, 0, 0);
  transform: translateX(-50%);
  z-index: 10;
}

.spin-button {
  padding: 12px 24px;
  font-size: 18px;
  background-color: #ffd900;
  color: rgb(0, 0, 0);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.5);

}

.spin-button:hover {
  background-color: #ffd000;

}

.spin-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  box-shadow: 0 0 20px rgba(255, 196, 0, 0.00001);

}

.nft-counts {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  max-width: 330px;
  max-height: 100px;
  padding: 20px;
  text-align: center;
  font-family: Arial, sans-serif;
  background-color: #ffffff;
  border-radius: 15px;
}

.nft-count {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nft-count img {
  width: 50px;
  height: 50px;
  margin-bottom: 5px;
}

.win-message {
  margin-top: 20px;
  padding: 7px;
  background-color: #23c030b4;
  border-radius: 5px;
  font-size: 15px;
  font-weight: bold;
}
</style>