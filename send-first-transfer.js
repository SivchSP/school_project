import { TonClient } from '@ton/ton';
import { Cell, internal, toNano, beginCell } from '@ton/core';
import { mnemonicToPrivateKey } from '@ton/crypto';
import * as fs from 'fs';
import { HighloadWalletV3 } from './wrappers/HighloadWalletV3.js';

async function sendFirstTransfer() {
    try {
        // Получаем аргументы командной строки
        const args = process.argv.slice(2);
        if (args.length < 2) {
            console.log('❌ Использование: node send-first-transfer.js <адрес_получателя> <сумма_в_TON>');
            console.log('Пример: node send-first-transfer.js EQD... 0.01');
            process.exit(1);
        }
        
        const destinationAddress = args[0];
        const amountTon = args[1];
        
        // Загружаем данные кошелька
        const walletData = JSON.parse(fs.readFileSync('.wallet.json', 'utf-8'));
        const mnemonic = walletData.mnemonic.split(' ');
        const keyPair = await mnemonicToPrivateKey(mnemonic);
        
        // Код контракта
        const CODE = Cell.fromBoc(Buffer.from(
            'b5ee9c7241021001000228000114ff00f4a413f4bcf2c80b01020120020d02014803040078d020d74bc00101c060b0915be101d0d3030171b0915be0fa4030f828c705b39130e0d31f018210ae42e5a4ba9d8040d721d74cf82a01ed55fb04e030020120050a02027306070011adce76a2686b85ffc00201200809001aabb6ed44d0810122d721d70b3f0018aa3bed44d08307d721d70b1f0201200b0c001bb9a6eed44d0810162d721d70b15800e5b8bf2eda2edfb21ab09028409b0ed44d0810120d721f404f404d33fd315d1058e1bf82325a15210b99f326df82305aa0015a112b992306dde923033e2923033e25230800df40f6fa19ed021d721d70a00955f037fdb31e09130e259800df40f6fa19cd001d721d70a00937fdb31e0915be270801f6f2d48308d718d121f900ed44d0d3ffd31ff404f404d33fd315d1f82321a15220b98e12336df82324aa00a112b9926d32de58f82301de541675f910f2a106d0d31fd4d307d30cd309d33fd315d15168baf2a2515abaf2a6f8232aa15250bcf2a304f823bbf2a35304800df40f6fa199d024d721d70a00f2649130e20e01fe5309800df40f6fa18e13d05004d718d20001f264c858cf16cf8301cf168e1030c824cf40cf8384095005a1a514cf40e2f800c94039800df41704c8cbff13cb1ff40012f40012cb3f12cb15c9ed54f80f21d0d30001f265d3020171b0925f03e0fa4001d70b01c000f2a5fa4031fa0031f401fa0031fa00318060d721d300010f0020f265d2000193d431d19130e272b1fb00b585bf03',
            'hex'
        ))[0];
        
        const client = new TonClient({
            endpoint: 'https://toncenter.com/api/v2/jsonRPC',
            apiKey: '799012f0eb0e8cbb554cb76efea226498cfe594ee4c1c2d77c6f5de58b23dd82'
        });
        
        const wallet = client.open(
            HighloadWalletV3.createFromConfig(
                {
                    publicKey: keyPair.publicKey,
                    subwalletId: walletData.subwalletId,
                    timeout: walletData.timeout,
                },
                CODE
            )
        );
        
        const address = wallet.address.toString({ bounceable: false, testOnly: false });
        console.log(`📍 Отправитель: ${address}`);
        console.log(`📍 Получатель: ${destinationAddress}`);
        console.log(`💰 Сумма: ${amountTon} TON`);
        
        // Проверяем баланс
        const balance = await client.getBalance(wallet.address);
        const balanceTon = Number(balance) / 1e9;
        console.log(`💰 Баланс отправителя: ${balanceTon} TON`);
        
        if (balanceTon < parseFloat(amountTon) + 0.01) {
            console.log('❌ Недостаточно средств для отправки + комиссии');
            process.exit(1);
        }
        
        console.log('');
        console.log('🚀 Отправляем транзакцию...');
        
        // Формируем сообщение для отправки
        const message = internal({
            to: destinationAddress,
            value: toNano(amountTon),
            bounce: false,
            body: beginCell()
                .storeUint(0, 32)  // op code для простого перевода
                .storeStringTail('Test transfer from Highload Wallet')
                .endCell()
        });
        
        // Отправляем через HighloadWalletV3
        // TODO: Здесь нужна полная реализация отправки
        console.log('⚠️ Для полноценной отправки требуется доработать метод sendExternalMessage');
        console.log('⚠️ Пока что транзакция не отправлена');
        console.log('');
        console.log('💡 Альтернатива: Используйте обычный кошелек для тестовой активации');
        console.log('или дождитесь готового решения для Highload Wallet');
        
    } catch (error) {
        console.error('❌ Ошибка:', error.message);
        console.error(error);
    }
}

sendFirstTransfer();