import TonWeb from 'tonweb';  

(async () => {  
    const provider = new TonWeb.HttpProvider('https://testnet.toncenter.com/api/v2/jsonRPC');  
    const tonweb = new TonWeb(provider);  

    // 1. Загружаем ключ администратора  
    const privateKey = new Uint8Array(Buffer.from('d41d0c2fef6ea013b56e9a09e20782b711a98015bfc06254541e52799c686ad1', 'hex'));  
    const keyPair = TonWeb.utils.nacl.sign.keyPair.fromSeed(privateKey);  

    // 2. Получаем адрес кошелька администратора  
    const WalletClass = tonweb.wallet.all['v3R2'];  
    const wallet = new WalletClass(provider, { publicKey: keyPair.publicKey, wc: 0 });  
    const walletAddress = await wallet.getAddress();  

    // 3. Формируем сообщение для контракта  
    const body = new TonWeb.boc.Cell();  
    body.bits.writeAddress(new TonWeb.utils.Address('0QDYpaokcR3aXrAStiMj2nPFdBlBymjgRhZQz3dNDDhSAVBs'));  
    body.bits.writeCoins(TonWeb.utils.toNano('1')); // 1 TON  

    // 4. Отправляем транзакцию  
    await wallet.methods.transfer({  
        secretKey: keyPair.secretKey,  
        toAddress: 'EQCm6we41JB5_a-bz581Yarp2WUc7btjWozHr-j9UaRgO6la',   // Куда переводим
        amount: TonWeb.utils.toNano('0.1'), // Газ  
        seqno: await wallet.methods.seqno().call(),  
        payload: body,  
        sendMode: 3,  
    }).send();  

    console.log('✅ Перевод инициирован!');  
})();  