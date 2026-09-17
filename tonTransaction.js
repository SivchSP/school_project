// tonTransaction.js
import { getHttpEndpoint } from "@orbs-network/ton-access";
import { mnemonicToWalletKey } from "@ton/crypto";
import { TonClient, WalletContractV4, internal } from "@ton/ton";

export async function sendTonTransaction(mnemonic, recipientAddress, amount, comment = "") {
    try {
        const key = await mnemonicToWalletKey(mnemonic.split(" "));
        const wallet = WalletContractV4.create({ publicKey: key.publicKey, workchain: 0 });

        const endpoint = await getHttpEndpoint({ network: "mainnet" });
        const client = new TonClient({ endpoint });

        const isDeployed = await client.isContractDeployed(wallet.address);
        if (!isDeployed) {
            throw new Error("Кошелек не развернут. Сначала отправьте на него немного TON");
        }

        const walletContract = client.open(wallet);
        const seqno = await walletContract.getSeqno();

        await walletContract.sendTransfer({
            secretKey: key.secretKey,
            seqno: seqno,
            messages: [
                internal({
                    to: recipientAddress,
                    value: amount.toString(),
                    body: comment,
                    bounce: false,
                })
            ]
        });

        let currentSeqno = seqno;
        while (currentSeqno === seqno) {
            await new Promise(resolve => setTimeout(resolve, 1500));
            currentSeqno = await walletContract.getSeqno();
        }

        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}