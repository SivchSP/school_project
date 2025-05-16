import { defineStore } from 'pinia'
import debounce from 'lodash.debounce'
import { updateScore } from '../../api/app'

const debouncedUpdateScore = debounce(updateScore, 500)

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
    boost: 0, // Теперь используем только boost
  }),
  getters: {
    level: (state) => computeLevelByScore(state.score),
    currentScore(state) {
      if (this.level.level === 0) {
        return state.score
      }
      return state.score - levelScores[this.level.level - 1]
    },
    // Добавляем геттер для вычисления значения клика
    clickValue: (state) => state.boost + 1
  },
  actions: {
    add() {
      if (!this.currentAccount) {
        console.warn('Не выбран аккаунт для начисления кликов')
        return
      }
      
      // Используем вычисляемое значение (boost + 1)
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
        this.setBoost(account.boost || 0)
        
        console.log('Account loaded:', {
          name: account.name,
          score: account.score,
          boost: account.boost
        })
      } else {
        this.resetAccount()
      }
    },
    resetAccount() {
      this.score = 0
      this.boost = 0
      this.currentAccount = null
    },
    clearAccount() {
      this.currentAccount = null
      this.setScore(0)
      this.setBoost(0)
    }
  },
})