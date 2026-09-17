// services/vercel-config.js

let config = null;
let configPromise = null;

// Функция для получения всех переменных из Vercel
export function getVercelConfig() {
    if (config) return Promise.resolve(config);
    
    if (configPromise) return configPromise;
    
    configPromise = fetch('/api/debug-env')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.environment) {
                config = data.environment;
                console.log('✅ Все переменные из Vercel загружены');
                return config;
            }
            throw new Error('Failed to load config');
        })
        .catch(error => {
            console.error('❌ Ошибка загрузки конфига:', error);
            throw error;
        });
    
    return configPromise;
}

// Получение конкретной переменной
export async function getEnvVar(key) {
    const config = await getVercelConfig();
    return config[key];
}