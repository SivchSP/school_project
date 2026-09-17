import { Address, TonClient, WalletContractV4, internal } from "@ton/ton";
import { keyPairFromSecretKey } from "@ton/crypto";

// ✅ Правильный приватный ключ (64 hex-символа)
const PRIVATE_KEY = Buffer.from("none", "hex");

async function sendMessage() {
    const client = new TonClient({ endpoint: "https://toncenter.com/api/v2/jsonRPC" });
    const keyPair = keyPairFromSecretKey(PRIVATE_KEY);
    
    const wallet = WalletContractV4.create({ 
        workchain: 0, 
        publicKey: keyPair.publicKey 
    });
    const contract = client.open(wallet);

    const messageBody = beginCell()
        .storeUint(0x12345678, 32)
        .storeStringTail("Hello")
        .endCell();

    await contract.sendTransfer({
        secretKey: keyPair.secretKey,
        seqno: await contract.getSeqno(),
        messages: [
            internal({
                to: "none",
                value: "0.05",
                body: messageBody
            })
        ]
    });
}

sendMessage();