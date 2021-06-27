package Project;


class Player extends User implements Comparable<Player> {

	private static int vipThreshold = 3;
	static final String welcomeMessage = "\nWelcome to the GameSystem Player";
	private int totalPoints;
	private int timesPlayed;
	
	
	Player(String name) {
		this(name, 0, 0);
	}
		
	Player(String name, int points, int history) {
		this.name = name;
		this.totalPoints = points;
		this.timesPlayed = history;
		GameSystem.addPlayer(this);
	}
	
	
	/*
	 *  Instance Methods
	 */
	
	int getTotal() {
		return this.totalPoints;
	}
	
	void incrementTotal(int number) {
		if (number >= 0) this.totalPoints += number;
	}
	
	void voidTotal() {
		this.totalPoints = 0;
	}
 	
	
	int getTimesPlayed() {
		return this.timesPlayed;
	}
	
	void incrementTimesPlayed() {
		this.timesPlayed++;
	}
		
	boolean isVIP() {
		if (this.getTimesPlayed() < vipThreshold) {
			return false;
		}
		return true;
	}
	
	@Override
	String welcomeMessage() {
		return welcomeMessage;
	}
	
	@Override
	void endSession() {
		this.incrementTotal(this.getPoints());
		this.voidPoints();
	}
	
	String save() {

		String vipString;
		if (this.isVIP()) vipString = "true";
		else vipString = "false";
		
		String details;
		details = this.getName() +";"+ this.getTotal() +";"+
					this.getTimesPlayed() +";"+ vipString +";\n";
		
		return details;
	}
		
	@Override
	public String toString() {
		return String.format("%-32s%10d", this.getName(), this.getTotal());
	}

	@Override
	public int compareTo(Player p) {
		int result = 0;
		if (this.getTotal() < p.getTotal()) {
			result = -1;
		}
		else if (this.getTotal() > p.getTotal()) {
			result = 1;
		}
		return result;
	}
	
}
