//package hw3;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;

/**
 * 
 * @author yanhui
 *
 */
public class LR {
	public static double overflow = 20;
	private static final String STOP_WORDS = ",a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,likely,may,me,might,most,must,my,neither,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your,";
	private static final String[] ALL_LABELS = {"Place", "Biomolecule", "other", "Device", "Event", "Agent", "Location", "Work", "Organisation", "TimePeriod", "ChemicalSubstance", "MeanOfTransportation", "Activity", "CelestialBody", "SportsSeason", "Species", "Person"};
	private static int[][] labels_A;
	private static double[][] labels_B;
	private static double[][] prev_weight;
	private static int[][] labels_k = new int[17][1];
	private static int vocabSize;
	
	public LR(int vocab_size){
		labels_A = new int[17][vocab_size];
		labels_B = new double[17][vocab_size];
		prev_weight = new double[17][vocab_size];
		vocabSize = vocab_size;
	}
	
	
	/**
	 * Safe sigmoid
	 * @param score
	 * @return
	 */
	protected double sigmoid(double score) {
		if (score > overflow) score = overflow;
		else if (score < -overflow) score = -overflow;
		double exp = Math.exp(score);
		return exp / (1 + exp);
		}
	
	/**
	 * change the document to features and remove the stop words
	 * convert the word to hashcode, allow for collisions
	 * @param cur_doc
	 * @return
	 */
	public static ArrayList<Integer> tokenizeDoc(String cur_doc) {
		String[] words = cur_doc.split("\\s+");
		ArrayList<Integer> tokens = new ArrayList<Integer>();
		for (int i = 0; i < words.length; i++) {
//			words[i] = words[i].replaceAll("\\W", "");
			String to_stop = "," + words[i] + ",";
			if (words[i].length() > 0 && !STOP_WORDS.contains(to_stop)) {
				int id = words[i].hashCode() % vocabSize;
				if (id < 0) id += vocabSize;
				tokens.add(id);
			}
		}
		return tokens;
	}
	
	/**
	 * Multiply the weight matrix with feature matrix
	 * @param weight
	 * @param x
	 * @return
	 */
	public double getProb(double[] weight, ArrayList<Integer> word_occur){
		double sum = 0.0;
		for(int word : word_occur){
			sum += weight[word];
		}
		return sum;
	}
	
	/**
	 * 
	 * @param vocabSize
	 * @param learningRate
	 * @param regular_coef
	 * @param iterations
	 * @param trainSize
	 * @throws IOException
	 */
	public void train(double learningRate, double regular_coef, int iterations, int trainSize) throws IOException{
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		//BufferedReader br = new BufferedReader(new FileReader("train_ite"));
		String line = null;
		int cnt = 0;
		int iterate = 0;
		
		while((line = br.readLine()) != null){
			String[] splitLine = line.split("\t");
			String labels = splitLine[1];
			String content = splitLine[2];
			ArrayList<Integer> features = tokenizeDoc(content);
			for(int label = 0; label < 17; label++){
				labels_k[label][0] ++;
				int y_value = labels.contains(ALL_LABELS[label]) ? 1 : 0;
				double weight_sum = getProb(labels_B[label], features);
				for(int word : features){
					labels_B[label][word] = labels_B[label][word] * Math.pow(1 - 2*learningRate*regular_coef, labels_k[label][0] - labels_A[label][word]);
					double p = sigmoid(weight_sum - prev_weight[label][word] + labels_B[label][word]);
					prev_weight[label][word] = labels_B[label][word];
					labels_B[label][word] = labels_B[label][word] + learningRate * (y_value - p);
					labels_A[label][word] = labels_k[label][0];
				}
			}
			cnt ++;
			if(cnt == trainSize){
				cnt = 0;
				iterate ++;
				learningRate = 0.5 / Math.pow(iterate, 2);
                                System.out.println(iterate);
			}
		}
	}
	
	public void test(String filename) throws IOException{
		BufferedReader br = new BufferedReader(new FileReader(filename));
		String line = null;
		int correct = 0;
		int testSize = 0;
		while((line = br.readLine()) != null){
			String[] splitLine = line.split("\t");
			String labels = splitLine[1];
			String content = splitLine[2];
            ArrayList<Integer> features = tokenizeDoc(content);
//			StringBuilder output = new StringBuilder();
			for(int label = 0; label < 17; label++){
				double p = sigmoid(getProb(labels_B[label], features));
//				output.append("," + ALL_LABELS[label] + "\t" + p);
				int y_value = labels.contains(ALL_LABELS[label]) ? 1 : 0;
				if((y_value == 1 && p >= 0.5) || (y_value == 0 && p < 0.5)){
					correct ++;
				}
			}
//			output.deleteCharAt(0);
//			System.out.println(output.toString());
			testSize ++;
		}
		double accuracy = (double) correct / (double) (testSize * 17);
		System.out.println(accuracy);
	}
	
	public static void main(String[] args) throws IOException {
		int vocabSize = Integer.parseInt(args[0]);
		double learningRate = Double.parseDouble(args[1]);
		double regular_coef = Double.parseDouble(args[2]);
		int iterations = Integer.parseInt(args[3]);
		int trainSize = Integer.parseInt(args[4]);
		String testFile = args[5];
		
		LR lr = new LR(vocabSize);
		lr.train(learningRate, regular_coef, iterations, trainSize);
		System.out.print(regular_coef + ": ");
		lr.test(testFile);
	}

}
