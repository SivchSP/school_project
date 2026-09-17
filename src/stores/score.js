import { defineStore } from 'pinia'
import debounce from 'lodash.debounce'
import { updateScore, getUserByName } from '../../api/app'
import supabase from '../../services/supabase'

// Простой кэш в памяти
const memoryCache = {
  userData: null,
  lastUpdate: null,
  isCached: false
}

// В score.js замените debouncedUpdateScore
const debouncedUpdateScore = debounce(async (score, userName) => {
  try {
    const updatedUser = await updateScore(score, userName)
    
    // После обновления счета обновляем локальное состояние
    // НЕ вызываем setCurrentAccount чтобы не перезаписать boost
    if (updatedUser) {
      // Только обновляем score, boost оставляем как есть
      const store = useScoreStore()
      store.score = score
      
      // Обновляем кэш
      if (memoryCache.userData) {
        memoryCache.userData.score = score
        memoryCache.lastUpdate = Date.now()
      }
      
      console.log('Score updated locally:', { score, currentBoost: store.boost })
    }
  } catch (error) {
    console.error('Error updating score:', error)
  }
}, 500)

const baseLevelScore = 25

const levels = new Array(1000)
  .fill(0)
  .map((_, i) => baseLevelScore * Math.pow(2, i))

const levelScores = levels.map((_, level) => {
  let sum = 0

  for (let [index, value] of levels.entries()) {
    if (index >= level) {
      return sum + value
    }
    sum += value
  }

  return sum
})

function computeLevelByScore(score) {
  for (let [index, value] of levelScores.entries()) {
    if (score <= value) {
      return {
        level: index,
        value: levels[index],
      }
    }
  }
}

export const useScoreStore = defineStore('score', {
  state: () => ({
    score: 0,
    currentAccount: null,
    boost: 0, // Значение по умолчанию
    isLoading: false,
    purchasedBoosts: {
      boost_1: false,
      boost_2: false,
      boost_3: false,
      boost_4: false,
      boost_5: false
    },
    // ДОБАВЛЕНО: Для пассивного дохода
    passiveIncome: 0,
    currentDiscount: 0,
    passiveIncomeInterval: null,
    lastIncomeUpdate: null
  }),
  
  getters: {
    level: (state) => computeLevelByScore(state.score),
    currentScore(state) {
      if (this.level.level === 0) {
        return state.score
      }
      return state.score - levelScores[this.level.level - 1]
    },
    clickValue: (state) => (state.boost || 0) + 1
  },
  
  actions: {
    // Получить данные из кэша
    getCachedData() {
      if (memoryCache.isCached && memoryCache.userData) {
        const now = Date.now()
        // Кэш действителен 30 секунд
        if (now - memoryCache.lastUpdate < 30000) {
          console.log('⚡ Используем кэшированные данные')
          return memoryCache.userData
        }
      }
      return null
    },
    
    // Сохранить данные в кэш
    cacheUserData(userData) {
      memoryCache.userData = { ...userData }
      memoryCache.lastUpdate = Date.now()
      memoryCache.isCached = true
      console.log('💾 Данные сохранены в кэш')
    },
    
    // Очистить кэш
    clearCache() {
      memoryCache.userData = null
      memoryCache.lastUpdate = null
      memoryCache.isCached = false
      console.log('🧹 Кэш очищен')
    },
    
    // ДОБАВЛЕНО: Метод для расчета накопленного пассивного дохода (как progress-bar)
    calculateOfflinePassiveIncome(userData) {
      if (!userData.passive_income || userData.passive_income <= 0) return 0;
      
      const now = new Date();
      const lastUpdate = new Date(userData.last_passive_income_update || userData.updated_at || userData.created_at);
      const secondsPassed = Math.floor((now - lastUpdate) / 1000);
      
      if (secondsPassed > 0) {
        const earnedIncome = userData.passive_income * secondsPassed;
        
        // Ограничиваем максимальный заработок (макс 24 часа)
        const maxEarned = userData.passive_income * 86400;
        const finalIncome = Math.min(earnedIncome, maxEarned);
        
        console.log(`💰 Offline passive income calculated: +${finalIncome} coins (${secondsPassed} seconds)`);
        return finalIncome;
      }
      
      return 0;
    },
    
    // Обновленная функция загрузки данных
    async loadAccountData(accountName) {
      if (!accountName) return
      
      // Сначала пробуем получить из кэша
      const cachedData = this.getCachedData()
      if (cachedData) {
        this.setCurrentAccount(cachedData)
        return
      }
      
      // Если нет в кэше, загружаем с сервера
      this.isLoading = true
      try {
        const userData = await getUserByName(accountName)
        if (userData) {
          // ДОБАВЛЕНО: Применяем оффлайн пассивный доход
          await this.applyOfflinePassiveIncome(userData)
          this.setCurrentAccount(userData)
          
          // Сохраняем в кэш
          this.cacheUserData(userData)
          
          // Загружаем данные о покупках бустов
          const initialBoosts = {
            boost_1: false,
            boost_2: false,
            boost_3: false,
            boost_4: false,
            boost_5: false
          }

          for (const key in initialBoosts) {
            if (userData[key] !== undefined) {
              this.purchasedBoosts[key] = userData[key]
            }
          }
          
          console.log('Account data loaded from server:', userData)
        }
      } catch (error) {
        console.error('Error loading account data:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    // ДОБАВЛЕНО: Простой метод для оффлайн пассивного дохода
    async applyOfflinePassiveIncome(userData) {
      if (!userData.passive_income || userData.passive_income <= 0) return;
      
      const now = new Date();
      const lastUpdate = new Date(userData.last_passive_income_update || userData.updated_at || userData.created_at);
      const secondsPassed = Math.floor((now - lastUpdate) / 1000);
      
      if (secondsPassed > 0) {
        const earnedIncome = userData.passive_income * secondsPassed;
        
        // Ограничиваем максимальный заработок (макс 24 часа)
        const maxEarned = userData.passive_income * 86400; // 24 часа
        const finalIncome = Math.min(earnedIncome, maxEarned);
        
        if (finalIncome > 0) {
          console.log(`💰 Offline passive income: +${finalIncome} coins (${secondsPassed} seconds)`);
          
          // Обновляем счет в базе
          const newScore = userData.score + finalIncome;
          await updateScore(newScore, userData.name);
          
          // Обновляем время последнего расчета
          await supabase
            .from('users')
            .update({ 
              last_passive_income_update: now.toISOString() 
            })
            .eq('name', userData.name);
          
          userData.score = newScore;
        }
      }
    },
    
    add() {
      if (!this.currentAccount) {
        console.warn('Не выбран аккаунт для начисления кликов')
        return
      }
      
      this.score += this.clickValue
      debouncedUpdateScore(this.score, this.currentAccount.name)
    },
    
    setScore(score) {
      this.score = score
    },
    
    setBoost(value) {
      this.boost = value
    },
    
    setCurrentAccount(account) {
      this.currentAccount = account
      if (account) {
        this.setScore(account.score || 0)
        
        // ВАЖНО: Не перезаписываем boost если он undefined в новых данных
        if (account.boost !== undefined && account.boost !== null) {
          this.setBoost(account.boost)
        }
        
        // ВОССТАНАВЛИВАЕМ purchasedBoosts из данных аккаунта
        const boostFields = ['boost_1', 'boost_2', 'boost_3', 'boost_4', 'boost_5']
        boostFields.forEach(field => {
          if (account[field] !== undefined) {
            this.purchasedBoosts[field] = account[field]
          }
        })
        
        // ДОБАВЛЕНО: Восстанавливаем пассивный доход
        if (account.passive_income !== undefined) {
          this.passiveIncome = account.passive_income
          this.startPassiveIncome()
        }
        
        console.log('Account loaded with boosts:', {
          name: account.name,
          score: account.score,
          boost: this.boost,
          purchasedBoosts: this.purchasedBoosts,
          passiveIncome: this.passiveIncome
        })
      } else {
        this.resetAccount()
      }
    },
    
    resetAccount() {
      this.score = 0
      this.boost = 0
      this.currentAccount = null
      this.passiveIncome = 0
      this.currentDiscount = 0
      this.stopPassiveIncome()
      this.purchasedBoosts = {
        boost_1: false,
        boost_2: false,
        boost_3: false,
        boost_4: false,
        boost_5: false
      }
      this.clearCache()
    },
    
    clearAccount() {
      this.currentAccount = null
      this.setScore(0)
      this.setBoost(0)
      this.passiveIncome = 0
      this.currentDiscount = 0
      this.stopPassiveIncome()
      this.clearCache()
    },
    
    // ДОБАВЛЕНО: Методы для работы с акциями
    async addPassiveIncome(amount) {
      this.passiveIncome += amount
      console.log(`💰 Passive income increased: +${amount}/sec, total: ${this.passiveIncome}/sec`)
      
      // Обновляем в базе данных
      if (this.currentAccount?.name) {
        await this.updatePassiveIncomeInDB()
      }
      
      this.startPassiveIncome()
    },
    
    applyDiscount(percentage) {
      this.currentDiscount = percentage
      console.log(`🎯 Discount applied: ${percentage}%`)
      
      // Скидка действует 5 минут
      setTimeout(() => {
        if (this.currentDiscount === percentage) {
          this.currentDiscount = 0
          console.log('🎯 Discount expired')
        }
      }, 5 * 60 * 1000) // 5 минут
    },
    
    // ДОБАВЛЕНО: Упрощенный метод обновления в БД
    async updatePassiveIncomeInDB() {
      if (!this.currentAccount?.name) return
      
      try {
        const { error } = await supabase
          .from('users')
          .update({ 
            passive_income: this.passiveIncome,
            last_passive_income_update: new Date().toISOString()
          })
          .eq('name', this.currentAccount.name)
          
        if (error) throw error
        console.log('✅ Passive income updated in database:', this.passiveIncome)
      } catch (error) {
        console.error('❌ Error updating passive income:', error)
      }
    },
    
    // ДОБАВЛЕНО: Упрощенный старт пассивного дохода
    startPassiveIncome() {
      if (this.passiveIncomeInterval || this.passiveIncome <= 0) return
      
      // Очищаем существующий интервал на всякий случай
      if (this.passiveIncomeInterval) {
        clearInterval(this.passiveIncomeInterval)
      }
      
      this.passiveIncomeInterval = setInterval(() => {
        if (this.passiveIncome > 0 && this.currentAccount?.name) {
          this.score += this.passiveIncome
          console.log(`💫 Passive income: +${this.passiveIncome} coins`)
          
          // Обновляем last_passive_income_update каждую минуту для точности оффлайн расчетов
          const now = new Date();
          if (!this.lastIncomeUpdate || (now - this.lastIncomeUpdate) > 60000) {
            this.updatePassiveIncomeInDB();
            this.lastIncomeUpdate = now;
          }
          
          // Обновляем счет в базе данных
          debouncedUpdateScore(this.score, this.currentAccount.name)
        }
      }, 1000)
    },
    
    stopPassiveIncome() {
      if (this.passiveIncomeInterval) {
        clearInterval(this.passiveIncomeInterval)
        this.passiveIncomeInterval = null
      }
    },
    
    // Обновленный метод покупки буста с учетом скидки
    async purchaseBoost(pack) {
      if (this.purchasedBoosts[pack.field] || this.score < pack.price) return false

      try {
        // Применяем скидку если есть
        const finalPrice = this.currentDiscount > 0 
          ? Math.floor(pack.price * (1 - this.currentDiscount / 100))
          : pack.price

        const newScore = this.score - finalPrice
        const newBoost = this.boost + pack.value

        console.log('Updating database:', {
          score: newScore,
          boost: newBoost,
          field: pack.field,
          originalPrice: pack.price,
          discountedPrice: finalPrice,
          discount: this.currentDiscount
        })

        const { data, error } = await supabase
          .from('users')
          .update({
            score: newScore,
            boost: newBoost,
            [pack.field]: true
          })
          .eq('name', this.currentAccount.name)
          .select()

        if (error) throw error

        console.log('Database updated successfully:', data)

        // Только после успешного обновления БД обновляем локальное состояние
        this.score = newScore
        this.boost = newBoost
        this.purchasedBoosts[pack.field] = true
        
        // Обновляем кэш
        if (memoryCache.userData) {
          memoryCache.userData.score = newScore
          memoryCache.userData.boost = newBoost
          memoryCache.userData[pack.field] = true
          memoryCache.lastUpdate = Date.now()
        }
        
        // Сбрасываем скидку после использования
        if (this.currentDiscount > 0) {
          this.currentDiscount = 0
          console.log('🎯 Discount used and reset')
        }

        return true
      } catch (error) {
        console.error('Error purchasing boost:', error)
        return false
      }
    }
  },
})