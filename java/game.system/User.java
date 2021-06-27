package Project;

class User {
	
	protected String name;
	static final String welcomeMessage = "\nPlaying as Guest, session will not be saved";
	protected int sessionPoints;
	protected boolean playedThisSession = false;
	
	User() {
		this.sessionPoints = 0;
		this.name = "Guest";
	}
	
	
	String getName() {
		return name;
	}
		
	String welcomeMessage() {
		return welcomeMessage;
	}
	
	int getPoints() {
		return this.sessionPoints;
	}
	
	void incrementPoints(int score) {
		if (score > 0) {
			this.sessionPoints += score;
		}
	}
	
	void voidPoints() {
		this.sessionPoints = 0;
	}
	
	boolean hasPlayedThisSession() {
		return playedThisSession;
	}
	
	void setPlayedThisSession() {
		playedThisSession = true;
	}
	
	void endSession() {}
	
	
	@Override
	public String toString() {
		return String.format("%-32s%10d", this.getName(), this.getPoints());
	}
}
