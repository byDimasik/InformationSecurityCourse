import kotlin.coroutines.experimental.buildSequence

/**
 * Class for converting cyphertext to HEX String
 *
 * @property text cyphertext
 * @property hexText cyphertext as HEX String
 */
class CypherText(val text: String) {
    private var hexText = text.flatMap { listOf("%02X".format(it.toInt())) }.joinToString("")

    override fun toString(): String {
        return hexText
    }
}


fun ksa(key : String) : Array<Int> {
    val s = Array(256) { i -> i }

    var j = 0
    for (i in 0..255) {
        j = (j + s[i] + key[i % key.length].toInt()) % 256
        s[i] = s[j].also { s[j] = s[i] }  // swap
    }

    return s
}


fun prga(s : Array<Int>) = buildSequence {
    var i = 0
    var j = 0

    while (true) {
        i = (i + 1   ) % 256
        j = (j + s[i]) % 256
        s[i] = s[j].also { s[j] = s[i] }

        val k = s[(s[i] + s[j]) % 256]

        yield(k)
    }
}


fun rc4(key : String, text : String) : CypherText {
    val sBlock = ksa(key)
    val prgaIterator = prga(sBlock).iterator()

    val cypherTextBuilder = StringBuilder()

    text.forEach { cypherTextBuilder.append(it.toInt().xor(prgaIterator.next()).toChar()) }

    return CypherText(cypherTextBuilder.toString())
}