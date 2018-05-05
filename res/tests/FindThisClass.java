package cyberdyne.skynet.vision;
import java.util.Collection;

// comment
class FindThisClass {
	/*
	  public int doNotFindThis() {
	  	return 1;
	  }
	  *
	  */

//kommentar
// kommentar
	static <T> void findThisFunction(T[] a, Collection<T> c) {
		for (T o : a) {
			c.add(o); // Correct
		}
    }

	double findThisFunction2(Object o) {
	    return 2.0;
	}
		/*
		// kommentar
		*/
}
