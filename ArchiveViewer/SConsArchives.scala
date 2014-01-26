import scala.xml._
import scala.collection.mutable.HashMap

/** Set of common English words to exclude from the word counting. */
val commonEnglishWords : Set[String] = "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(",").toSet

/** Simplify a String by removing all non-alphanumerical chars. */
def defaultSimplify(word : String) : String =
{
    return word.replaceAll("[^\\p{L}\\p{Nd}]", " ")
}

/** A single message in a Thread. */
case class SConsMessage(val header : String,
                   val author : String,
                   val fullname : String,
                   val date : String,
                   val content : String)
{

    /** Scan the content of the message and update word counts with it. */ 
    def collectWordCounts(wordCounts : HashMap[String, Int],
                          excludeWords : Set[String],
                          simplifyString : String => String = defaultSimplify) 
    {
        // Simplify content and split it into words
        val words = simplifyString(this.content).split("\\s").toList.map(_.asInstanceOf[String])
        // Process each word and update count hash
        words.foreach(w => if (!w.isEmpty && !excludeWords.contains(w.toLowerCase()))
                           {
                               if (wordCounts.contains(w))
                                   wordCounts(w) += 1
                               else
                                   wordCounts += (w -> 1)
                           }
                     )
    }
}

/** A single thread, containing one or more messages. */
case class SConsThread(val html : String,
                  val id : String,
                  val issue : String,
                  val messages : Seq[SConsMessage])
{
    /** Scan all contained messages und update word counts accordingly. */
    def collectWordCounts(wordCounts : HashMap[String, Int],
                          excludeWords : Set[String]) 
    {
        this.messages.foreach(m => m.collectWordCounts(wordCounts, excludeWords))
    }

}

/** Set of all threads in a mailing list like "devel" or "user". */
class SConsThreadList(val fpath : String)
{
    // Parse the given XML file
    val domElems = scala.xml.XML.loadFile(fpath)
    val threads = (domElems \ "thread").map { thread =>
                    val html = (thread \ "html").text
                    val id = (thread \ "id").text
                    val issue = (thread \ "issue").text
                    val msglist = (thread \ "messages" \ "message").map {message =>

                      val header = (message \ "header").text
                      val author = (message \ "author").text
                      val fullname = (message \ "fullname").text
                      val date = (message \ "date").text
                      val content = (message \ "content").text
                      SConsMessage(header, author, fullname, date, content)
                    }
                    SConsThread(html, id, issue, msglist)
                  }

    /** Return a HashMap that results from counting the occurence of each word. */
    def getWordCounts(excludeWords : Set[String]) : HashMap[String, Int] =
    {
        var wordCounts = new HashMap[String, Int]
        threads.foreach(t => t.collectWordCounts(wordCounts, excludeWords))
        return wordCounts        
    }
}



val dev = new SConsThreadList("devel.xml")
println("Developer threads: "+dev.threads.size)

val user = new SConsThreadList("user.xml")
println("User threads: "+user.threads.size)
println(user.getWordCounts(commonEnglishWords).toList sortBy {_._2})




