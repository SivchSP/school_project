import supabase from '/services/supabase';

// В отдельном файле, например subscriptions.js
const activeSubscriptions = new Map();

export const subscribeToChannel = (channelName, callback) => {
  if (activeSubscriptions.has(channelName)) {
    console.log(`Подписка ${channelName} уже активна`);
    return;
  }
  
  const channel = supabase.channel(channelName)
    .on('postgres_changes', { event: '*', schema: 'public', table: 'market' }, callback)
    .subscribe();
  
  activeSubscriptions.set(channelName, channel);
};

export const unsubscribeFromChannel = (channelName) => {
  if (activeSubscriptions.has(channelName)) {
    supabase.removeChannel(activeSubscriptions.get(channelName));
    activeSubscriptions.delete(channelName);
  }
};