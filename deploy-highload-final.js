import pkg from '@ton/ton';
import pkgCore from '@ton/core';
import { mnemonicToPrivateKey } from '@ton/crypto';
import * as fs from 'fs';

const { TonClient, WalletContractV4, internal } = pkg;
const { Address, toNano, beginCell, contractAddress } = pkgCore;

async function deployHighload() {
    try {
        // Загружаем данные
        const highloadData = JSON.parse(fs.readFileSync('.wallet.json', 'utf-8'));
        const mnemonic = highloadData.mnemonic.split(' ');
        const keyPair = await mnemonicToPrivateKey(mnemonic);
        
        const client = new TonClient({
            endpoint: 'https://toncenter.com/api/v2/jsonRPC',
            apiKey: '799012f0eb0e8cbb554cb76efea226498cfe594ee4c1c2d77c6f5de58b23dd82'
        });
        
        // Код контракта Highload Wallet
        const CODE = pkgCore.Cell.fromBoc(Buffer.from(
            'b5ee9c7241021001000228000114ff00f4a413f4bcf2c80b01020120020d02014803040078d020d74bc00101c060b0915be101d0d3030171b0915be0fa4030f828c705b39130e0d31f018210ae42e5a4ba9d8040d721d74cf82a01ed55fb04e030020120050a02027306070011adce76a2686b85ffc00201200809001aabb6ed44d0810122d721d70b3f0018aa3bed44d08307d721d70b1f0201200b0c001bb9a6eed44d0810162d721d70b15800e5b8bf2eda2edfb21ab09028409b0ed44d0810120d721f404f404d33fd315d1058e1bf82325a15210b99f326df82305aa0015a112b992306dde923033e2923033e25230800df40f6fa19ed021d721d70a00955f037fdb31e09130e259800df40f6fa19cd001d721d70a00937fdb31e0915be270801f6f2d48308d718d121f900ed44d0d3ffd31ff404f404d33fd315d1f82321a15220b98e12336df82324aa00a112b9926d32de58f82301de541675f910f2a106d0d31fd4d307d30cd309d33fd315d15168baf2a2515abaf2a6f8232aa15250bcf2a304f823bbf2a35304800df40f6fa199d024d721d70a00f2649130e20e01fe5309800df40f6fa18e13d05004d718d20001f264c858cf16cf8301cf168e1030c824cf40cf8384095005a1a514cf40e2f800c94039800df41704c8cbff13cb1ff40012f40012cb3f12cb15c9ed54f80f21d0d30001f265d3020171b0925f03e0fa4001d70b01c000f2a5fa4031fa0031f401fa0031fa00318060d721d300010f0020f265d2000193d431d19130e272b1fb00b585bf03',
            'hex'
        ))[0];
        
        // Создаем data cell
        const data = beginCell()
            .storeBuffer(keyPair.publicKey)
            .storeUint(highloadData.subwalletId, 32)
            .storeUint(highloadData.timeout, 22)
            .endCell();
        
        const stateInit = { code: CODE, data: data };
        const highloadAddress = contractAddress(0, stateInit);
        
        console.log(`📍 Highload адрес (EQ): ${highloadAddress.toString({ bounceable: true, testOnly: false })}`);
        console.log(`📍 Highload адрес (UQ): ${highloadAddress.toString({ bounceable: false, testOnly: false })}`);
        
        // Создаем обычный кошелек V4
        const walletV4 = WalletContractV4.create({
            publicKey: keyPair.publicKey,
            workchain: 0
        });
        
        const walletV4Contract = client.open(walletV4);
        const v4Address = walletV4Contract.address.toString();
        
        console.log(`📍 Обычный кошелек V4: ${v4Address}`);
        
        // Проверяем баланс V4
        const v4Balance = await client.getBalance(walletV4Contract.address);
        console.log(`💰 Баланс V4: ${Number(v4Balance) / 1e9} TON`);
        
        if (Number(v4Balance) < toNano('0.05')) {
            console.log('❌ Недостаточно средств на V4 кошельке');
            process.exit(1);
        }
        
        // Проверяем текущий статус Highload кошелька
        const currentState = await client.getContractState(highloadAddress);
        console.log(`📊 Текущий статус Highload: ${currentState.state}`);
        
        if (currentState.state === 'active') {
            console.log('✅ Highload кошелек уже активен!');
            return;
        }
        
        console.log('🚀 Отправляем транзакцию для активации Highload кошелька...');
        
        // Самый простой способ: отправить 0.001 TON с комментарием
        // Это создаст внешнее сообщение и развернет контракт
        const seqno = await walletV4Contract.getSeqno();
        
        const transfer = await walletV4Contract.sendTransfer({
            seqno: seqno,
            secretKey: keyPair.secretKey,
            messages: [
                internal({
                    to: highloadAddress,
                    value: toNano('0.001'),
                    body: beginCell()
                        .storeUint(0, 32)
                        .storeStringTail('Deploy Highload Wallet')
                        .endCell(),
                    bounce: false
                })
            ]
        });
        
        console.log('✅ Транзакция отправлена!');
        console.log(`🔗 https://tonscan.org/tx/${transfer}`);
        
        console.log('⏳ Ждем 30 секунд для развертывания...');
        await new Promise(resolve => setTimeout(resolve, 30000));
        
        // Проверяем статус
        const newState = await client.getContractState(highloadAddress);
        console.log(`📊 Новый статус Highload кошелька: ${newState.state}`);
        
        if (newState.state === 'active') {
            console.log('🎉 УСПЕХ! Highload кошелек активирован!');
            
            const balance = await client.getBalance(highloadAddress);
            console.log(`💰 Баланс Highload: ${Number(balance) / 1e9} TON`);
            
            // Обновляем файл
            const updatedData = {
                ...highloadData,
                address: highloadAddress.toString({ bounceable: false, testOnly: false }),
                addressBounceable: highloadAddress.toString({ bounceable: true, testOnly: false }),
                isActive: true
            };
            fs.writeFileSync('.wallet.json', JSON.stringify(updatedData, null, 2));
            console.log('✅ Файл .wallet.json обновлен');
        } else {
            console.log('⚠️ Статус остался:', newState.state);
            console.log('💡 Возможно, нужно подождать еще или проверить в обозревателе');
        }
        
    } catch (error) {
        console.error('❌ Ошибка:', error.message);
        if (error.stack) {
            console.error(error.stack);
        }
    }
}

deployHighload();