import java.util.UUID


/**
 * This program generate random 256 bit key and encrypt text in $plaintext variable according to RC4 algorithm
 */
fun main(argv : Array<String>) {
    val key       = UUID.randomUUID().toString().filter { it != '-' }.take(256 / 8) // 256-bit random key
    val plaintext = "Plaintext"

    val cypherText   = rc4(key, plaintext)
    val decypherText = rc4(key, cypherText.text).text

    println("KEY       = $key")
    println("PLAINTEXT = $plaintext")

    beautyPrint("ENCRYPTED TEXT START", cypherText.toString(), "ENCRYPTED TEXT END")
    beautyPrint("DECRYPTED TEXT START", decypherText, "DECRYPTED TEXT END")
    beautyPrint("IS CORRECT", (decypherText == plaintext).toString().capitalize(), "")
}