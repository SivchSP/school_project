import { TonConnectUI } from '@tonconnect/ui'

let tonConnectInstance = null

export const initTonConnect = async (buttonId) => {
  // Если экземпляр уже существует, просто обновляем кнопку
  if (tonConnectInstance) {
    tonConnectInstance.uiOptions = {
      ...tonConnectInstance.uiOptions,
      buttonRootId: buttonId
    }
    return tonConnectInstance
  }

  const element = document.getElementById(buttonId)
  if (!element) {
    throw new Error(`Element with id "${buttonId}" not found`)
  }

  tonConnectInstance = new TonConnectUI({
    manifestUrl: 'https://raw.githubusercontent.com/SivchSP/Manifest/main/tonconnect-manifest.json',
    buttonRootId: buttonId,
    language: 'en',
    uiPreferences: {
      theme: 'DARK',
      borderRadius: 'm'
    },
    restoreConnection: true
  })

  await tonConnectInstance.uiReady
  return tonConnectInstance
}

export const getTonConnect = () => {
  if (!tonConnectInstance) {
    throw new Error('TonConnect not initialized')
  }
  return tonConnectInstance
}

// Очистка при демонтировании
export const disconnectTonConnect = async () => {
  if (tonConnectInstance) {
    // Не отключаемся полностью, чтобы сохранить состояние
    tonConnectInstance.uiOptions = {
      ...tonConnectInstance.uiOptions,
      buttonRootId: undefined
    }
  }
}