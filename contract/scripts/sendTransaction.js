import { Address, beginCell, toNano } from '@ton/core';
import { TonClient, WalletContractV4 } from '@ton/ton';
import dotenv from 'dotenv';

// Загружаем переменные окружения
dotenv.config();

// Основные переменные
const contractAddress = 'EQBHFSVxryp_RN1ZcbyO1u8OJ4RulQEMe8VZCDYZ1_OJcHqP'; // Замените на адрес вашего контракта
const recipientAddress = 'UQCm6we41JB5_a-bz581Yarp2WUc7btjWozHr-j9UaRgO_Sf'; // Адрес получателя перевода
const amountToSend = '1.5'; // Сумма в TON
const senderMnemonic = process.env.MNEMONIC; // Мнемоника из .env

async function main() {
    // Инициализация клиента
    const client = new TonClient({
        endpoint: 'https://toncenter.com/api/v2/jsonRPC' // или другой endpoint
    });

    // Инициализация кошелька
    const wallet = WalletContractV4.create({
        workchain: 0,
        publicKey: keyPair.publicKey,
    });
    
    // Подготовка тела сообщения
    const messageBody = beginCell()
        .storeUint(1, 32) // op = 1 (наша операция перевода)
        .storeCoins(toNano(amountToSend)) // сумма в нанотоннах
        .storeAddress(Address.parse(recipientAddress)) // адрес получателя
        .endCell();

    // Отправка сообщения
    await client.sendExternalMessage(wallet, {
        to: Address.parse(contractAddress),
        value: toNano('0.1'), // газ
        body: messageBody
    });

    console.log('Транзакция отправлена!');
}

main().catch(console.error);