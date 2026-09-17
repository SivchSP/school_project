// services/supabase.js
import { createClient } from '@supabase/supabase-js'

// Определяем, где выполняется код
const isServer = typeof window === 'undefined'

// Базовые переменные
const SUPABASE_URL = 'https://nohkjfzicycrdyjastxn.supabase.co'

// Выбираем ключ в зависимости от окружения
let SUPABASE_KEY

if (isServer) {
    // На сервере - используем SERVICE_ROLE (из переменных окружения)
    SUPABASE_KEY = process.env.SERVICE_ROLE
    
    if (!SUPABASE_KEY) {
        console.error('❌ SERVICE_ROLE not set on server!')
    }
} else {
    // В браузере - используем ANON ключ (публичный)
    SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vaGtqZnppY3ljcmR5amFzdHhuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxODg2MTcsImV4cCI6MjA3NTc2NDYxN30.1Vxvd2fi7tcUKaiTYv8uzO6KTu6fAgXfOw-cjZKpOBA'
}

// Создаем клиент
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// На сервере - отключаем авто-обновление токенов
if (isServer) {
    supabase.auth.onAuthStateChange = () => {}
}

export default supabase