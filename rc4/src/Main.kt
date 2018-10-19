import java.util.UUID


/**
 * This program generate random 256 bit key and encrypt text in resources/plaintext.txt file according to RC4 algorithm
 */
fun main(args : Array<String>) {
    val key = UUID.randomUUID().toString().filter { it != '-' }.take(256 / 8) // 256-bit random key

    rc4(key, "resources/plaintext.txt", "resources/cyphertext.txt")
    rc4(key, "resources/cyphertext.txt", "resources/decyphertext.txt")

    println("Key: $key")
}