import javafx.animation.FadeTransition;
import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.chart.CategoryAxis;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.scene.shape.Rectangle;
import javafx.stage.Stage;
import javafx.util.Duration;
import weather.Period;
import java.text.SimpleDateFormat;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Scanner;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;
import javafx.scene.control.ScrollPane;


public class JavaFX extends Application {
	private TextField temperature;
	private TextArea weather;
	private TextField precipitation;
	private String chosenCity = "";
	private int gridX = 0, gridY = 0;
	private char Unit = 'F';
	private ArrayList<Period> currentForecast;
	private ArrayList<Period> HourlyForecast;

	private char Theme = 'A';

	private int currentTheme;
	private int maxTheme = 3;

	private ImageView backgroundImageView;


	private final int SCENE_WIDTH = 700;
	private final int SCENE_HEIGHT = 700;

	private Scene mainScene;

	private Button UnitButton,ClearButton,ThemeButton,NextThemeButton,LastThemeButton;


	private MenuButton menuButton;

	public static void main(String[] args) {
		launch(args);
	}

	@Override
	public void start(Stage primaryStage) throws Exception {
		primaryStage.setTitle("ClimaSense");

		URL cityUrl = getClass().getResource("/weather_backgrounds/city.gif");
		if (cityUrl == null) {
			System.err.println("Resource not found: /weather_backgrounds/city.gif");
		} else {
			System.out.println("Found resource: " + cityUrl);
		}

		StackPane stack = new StackPane();

		Image cityImage = new Image(getClass().getResourceAsStream("/weather_backgrounds/city.gif"));
		backgroundImageView = new ImageView(cityImage);
		backgroundImageView.setFitWidth(SCENE_WIDTH);
		backgroundImageView.setFitHeight(SCENE_HEIGHT);
		backgroundImageView.setPreserveRatio(false);
		backgroundImageView.setSmooth(true);
		backgroundImageView.setCache(true);

		menuButton = new MenuButton("Choose City");

		temperature = new TextField();
		temperature.setAlignment(Pos.CENTER);
		temperature.setPromptText("Temperature");
		temperature.setEditable(false);

		weather = new TextArea();
		weather.getStyleClass().add("text-area");
		weather.setWrapText(true);
		weather.setPromptText("Weather");
		weather.setEditable(false);
		weather.setMaxWidth(Double.MAX_VALUE);
		weather.setPrefWidth(500); // or some width that fits longer text
		weather.setMaxWidth(Double.MAX_VALUE);

		precipitation = new TextField();
		precipitation.setAlignment(Pos.CENTER);
		precipitation.setPromptText("Probability of Precipitation");
		precipitation.setEditable(false);

		UnitButton = new Button("°F");
		UnitButton.setOnAction(event -> {
			if(UnitButton.getText().equals("°F")){
				UnitButton.setText("°C");
				Unit = 'C';
				if(!temperature.getText().equals("Temperature")){
					temperature.setText(getTemperature(currentForecast.get(0).temperature) + "°" + Unit);
				}
			}
			else{
				UnitButton.setText("°F");
				Unit = 'F';
				if(!temperature.getText().equals("Temperature")){
					temperature.setText(getTemperature(currentForecast.get(0).temperature) + "°" + Unit);
				}
			}
		});
		UnitButton.setOpacity(4);
		UnitButton.setId("BigButtons");

		ClearButton = new Button("Clear History");
		ClearButton.setOnAction(event -> clearHistory());

		ThemeButton = new Button("Animated");
		ThemeButton.setOnAction(event -> {
			if (Theme == 'A') {
				ThemeButton.setText("Simple");
				NextThemeButton.setDisable(false);
				LastThemeButton.setDisable(false);
				currentTheme = 1;
				mainScene.getStylesheets().clear();
				mainScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
				Theme = 'S';
				stack.getChildren().remove(backgroundImageView);
			}

			else{
				ThemeButton.setText("Animated");
				NextThemeButton.setDisable(true);
				LastThemeButton.setDisable(true);
				currentTheme = 0;
				Theme = 'A';
				stack.getChildren().add(0,backgroundImageView);
				mainScene.getStylesheets().clear();
				mainScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
			}
		});

		NextThemeButton = new Button("-->");
		NextThemeButton.setDisable(true);
		NextThemeButton.setOnAction(event -> {
			if(currentTheme == maxTheme) currentTheme = 0;
			currentTheme++;
			mainScene.getStylesheets().clear();
			mainScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
		});

		LastThemeButton = new Button("<--");
		LastThemeButton.setDisable(true);
		LastThemeButton.setOnAction(event -> {
			if(currentTheme == 1) currentTheme = maxTheme+1;
			currentTheme--;
			mainScene.getStylesheets().clear();
			mainScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
		});

		HBox ThemeBox = new HBox(10,LastThemeButton,ThemeButton,NextThemeButton);
		ThemeBox.setAlignment(Pos.CENTER);
		MenuItem chooseChicago = new MenuItem("Chicago (IL)");
		MenuItem chooseNYC = new MenuItem("New York City (NY)");
		MenuItem chooseHouston = new MenuItem("Houston (TX)");

		chooseChicago.setOnAction(e -> updateWeather(menuButton, "Chicago (IL)", "LOT", 76, 73));
		chooseNYC.setOnAction(e -> updateWeather(menuButton, "New York City (NY)", "OKX", 33, 35));
		chooseHouston.setOnAction(e -> updateWeather(menuButton, "Houston (TX)", "HGX", 65, 97));MenuItem customLocation = new MenuItem("Enter Custom Location");
		menuButton.getItems().add(customLocation);

		customLocation.setOnAction(e -> showCustomLocationInput());

		menuButton.getItems().addAll(chooseChicago, chooseNYC, chooseHouston);

		loadCustomLocations();

		Button forecastButton = new Button("5-Day Forecast");
		forecastButton.setOnAction(e -> {
			if (currentForecast != null && !currentForecast.isEmpty()) {
				showForecastScene(primaryStage);
			} else {
				Alert alert = new Alert(Alert.AlertType.INFORMATION);
				alert.setTitle("No Data");
				alert.setHeaderText(null);
				alert.setContentText("Please select a city to load the forecast first.");
				alert.showAndWait();
			}
		});

		Button detailedForecastButton = new Button( "Detailed Forecast");
		detailedForecastButton.setOnAction(e -> {
			if (currentForecast != null && !currentForecast.isEmpty()) {
				showDetailedForecastScene(primaryStage);
			}
			else{
				Alert alert = new Alert(Alert.AlertType.INFORMATION);
				alert.setTitle("No Data");
				alert.setHeaderText(null);
				alert.setContentText("Please select a city to load the forecast first.");
				alert.showAndWait();
			}
		});

		VBox vbox = new VBox(20, temperature, weather,precipitation);
		vbox.setAlignment(Pos.TOP_CENTER);
		vbox.setPadding(new Insets(20, 0, 0, 0));

		Region leftSpacer = new Region();
		Region rightSpacer = new Region();

		HBox topHbox = new HBox(10,UnitButton,leftSpacer,menuButton,rightSpacer,ClearButton);
		topHbox.setAlignment(Pos.CENTER);
		HBox.setHgrow(leftSpacer, Priority.ALWAYS);
		HBox.setHgrow(rightSpacer, Priority.ALWAYS);

		HBox bottomHbox =  new HBox(30,ThemeBox);
		bottomHbox.setAlignment(Pos.CENTER);




		VBox leftVBox = new VBox(80,forecastButton,detailedForecastButton,new Label(""),new Label(""));
		leftVBox.setAlignment(Pos.CENTER);

		HBox hbox = new HBox(vbox);
		hbox.setAlignment(Pos.CENTER);
		HBox.setHgrow(topHbox, Priority.ALWAYS);


		BorderPane borderPane = new BorderPane();

		StackPane topPane = new StackPane();
		topPane.getStyleClass().add("top-pane");
		topPane.getChildren().add(topHbox);

		StackPane bottomPane = new StackPane();
		bottomPane.getStyleClass().add("bottom-pane");
		bottomPane.getChildren().add(bottomHbox);

		StackPane leftPane = new StackPane();
		leftPane.getStyleClass().add("left-pane");
		leftPane.getChildren().add(leftVBox);


		Pane rightPane = new Pane();
		rightPane.getStyleClass().add("right-pane");

		StackPane centerPane = new StackPane();
		centerPane.getStyleClass().add("center-pane");
		centerPane.getChildren().add(hbox);

		borderPane.setTop(topPane);
		borderPane.setBottom(bottomPane);
		borderPane.setLeft(leftPane);
		borderPane.setRight(rightPane);
		borderPane.setCenter(centerPane);


		stack.getChildren().addAll(backgroundImageView, borderPane);

		mainScene = new Scene(stack, SCENE_WIDTH, SCENE_HEIGHT);
		mainScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
		primaryStage.setScene(mainScene);
		primaryStage.show();
	}

	// returns the temp in terms of the current unit
	// use this EVERY time you use p.temperature to get accurate units
	// like getTemperature(p.temperature)
	private int getTemperature(int FTemp) {
		if(Unit == 'F'){
			return FTemp;
		}
		else{
			double celcius = (5.0 / 9.0) * (FTemp - 32);
			return (int) Math.round(celcius);
		}
	}

	private void updateWeather(MenuButton menuButton, String cityName, String cityCode, int x, int y) {
		menuButton.setText(cityName);
		chosenCity = cityCode;
		gridX = x;
		gridY = y;

		ArrayList<Period> forecast = MyWeatherAPI.getForecast(chosenCity, gridX, gridY);
		currentForecast = forecast;
		HourlyForecast = MyWeatherAPI.getForecastHourly(chosenCity,gridX,gridY);

		if (forecast == null || forecast.isEmpty()) {
			temperature.setText("Failed to load forecast");
		} else {
			temperature.setText(getTemperature(forecast.get(0).temperature) + "°" + Unit);
			weather.setText(forecast.get(0).detailedForecast);
			precipitation.setText(String.valueOf(forecast.get(0).probabilityOfPrecipitation.value+"%"));
			fadeBackground(getBackground(forecast.get(0).shortForecast));
		}
	}

	private void fadeBackground(String imageFile) {
		URL imageUrl = getClass().getResource("/weather_backgrounds/" + imageFile);
		if (imageUrl == null) {
			System.err.println("Resource not found: /weather_backgrounds/" + imageFile);
			return;
		} else {
			System.out.println("Found resource: " + imageUrl);
		}

		Image newImage = new Image(getClass().getResourceAsStream("/weather_backgrounds/" + imageFile));

		FadeTransition fadeOut = new FadeTransition(Duration.seconds(1), backgroundImageView);
		fadeOut.setFromValue(1);
		fadeOut.setToValue(0);
		fadeOut.setOnFinished(e -> {
			backgroundImageView.setImage(newImage);
			FadeTransition fadeIn = new FadeTransition(Duration.seconds(1), backgroundImageView);
			fadeIn.setFromValue(0);
			fadeIn.setToValue(1);
			fadeIn.play();
		});
		fadeOut.play();
	}

	// Updated forecast scene method that includes a line chart below the day descriptions
	private void showForecastScene(Stage primaryStage) {
		// Create a background image view using the current image for consistency
		ImageView forecastBackground = new ImageView(backgroundImageView.getImage());
		forecastBackground.setFitWidth(SCENE_WIDTH);
		forecastBackground.setFitHeight(SCENE_HEIGHT);
		forecastBackground.setPreserveRatio(false);
		forecastBackground.setSmooth(true);

		VBox forecastBox = new VBox(20);
		forecastBox.setAlignment(Pos.TOP_CENTER);
		forecastBox.setPadding(new Insets(20, 0, 0, 0));

		Label titleLabel = new Label(menuButton.getText() + " 5-Day Forecast");
		titleLabel.setId("TitleLabels");
		forecastBox.getChildren().add(titleLabel);

		// Use a FlowPane to wrap forecast day nodes if they don't all fit in one row
		FlowPane forecastsFlow = new FlowPane();
		forecastsFlow.setHgap(20);
		forecastsFlow.setVgap(20);
		forecastsFlow.setAlignment(Pos.CENTER);

		// Prepare axes for the line chart:
		// x-axis for days (categorical) and y-axis for temperature (numeric)
		CategoryAxis xAxis = new CategoryAxis();
		xAxis.setLabel("Day");
		NumberAxis yAxis = new NumberAxis();
		yAxis.setLabel("Temperature");

		// Create the line chart with x axis as Category and y axis as Number
		LineChart<String, Number> lineChart = new LineChart<>(xAxis, yAxis);
		lineChart.setTitle("Temperature Trend");
		lineChart.setLegendVisible(false);
		lineChart.setCreateSymbols(true); // Show data points

		XYChart.Series<String, Number> series = new XYChart.Series<>();

		// Collect day names to set the x-axis categories
		ObservableList<String> dayNames = FXCollections.observableArrayList();

		int count = 0;
		for (Period p : currentForecast) {
			if (p.isDaytime && count < 5) {
				// Create a VBox for each day's forecast details
				VBox dayForecast = new VBox(10);
				dayForecast.setAlignment(Pos.CENTER);

				Button dayButton = new Button(p.name);
				dayButton.setOnAction(e -> detailedDayScene(primaryStage,p));

				Label tempLabel = new Label(getTemperature(p.temperature) + "°" + Unit);

				Label forecastLabel = new Label(p.shortForecast);

				dayForecast.getChildren().addAll(dayButton, tempLabel, forecastLabel);
				forecastsFlow.getChildren().add(dayForecast);

				// Add the data point with x = day name and y = temperature
				series.getData().add(new XYChart.Data<>(p.name, getTemperature(p.temperature)));
				dayNames.add(p.name);
				count++;
			}
		}

		if (count == 0) {
			Label noDataLabel = new Label("No forecast data available.");
			noDataLabel.setStyle("-fx-font-size: 18px; -fx-text-fill: black;");
			forecastBox.getChildren().add(noDataLabel);
		} else {
			forecastBox.getChildren().add(forecastsFlow);
			// Set the x-axis categories so the days are displayed in order
			xAxis.setCategories(dayNames);
			lineChart.getData().add(series);
			// Optionally, set a preferred height for the chart so it remains visible
			lineChart.setPrefHeight(300);
			forecastBox.getChildren().add(lineChart);
		}

		// Back button to return to the main scene
		Button backButton = new Button("Back");
		backButton.setOnAction(e -> primaryStage.setScene(mainScene));
		forecastBox.getChildren().add(backButton);

		StackPane forecastStack = new StackPane();
		forecastStack.getChildren().add(forecastBox);
		forecastStack.getStyleClass().add("stack-pane");

		if(Theme == 'A') forecastStack.getChildren().add(0,forecastBackground);

		Scene forecastScene = new Scene(forecastStack, SCENE_WIDTH, SCENE_HEIGHT);
		forecastScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());
		primaryStage.setScene(forecastScene);
	}

	//returns an ImageView with the icon from the URL string, or sets
	//default image if error occurs
	ImageView loadIcon(String iconUrl){
		Image image = new Image(iconUrl,true);
		ImageView IconImage = new ImageView(image);
		image.errorProperty().addListener((obs, oldError, newError) -> {
			if (newError) {
				System.out.println("Failed to load image: " + iconUrl);
				// set a default image
				IconImage.setImage(new Image (getClass().getResourceAsStream("/weather_backgrounds/sun.png")));

			}
		});
		return IconImage;
	}


	//Updated forcast scene that includes detailed hourly information about the location
	private void showDetailedForecastScene(Stage primaryStage) {

		//load current image as background
		ImageView forecastBackground = new ImageView(backgroundImageView.getImage());
		forecastBackground.setFitWidth(SCENE_WIDTH);
		forecastBackground.setFitHeight(SCENE_HEIGHT);
		forecastBackground.setPreserveRatio(false);
		forecastBackground.setSmooth(true);

		Label titleLabel = new Label(menuButton.getText() + " Detailed Forecast");
		titleLabel.setId("TitleLabels");
		Label hourlyLabel = new Label("Hourly Forecast");
		hourlyLabel.setId("SubLabels");

		VBox compassBox = new VBox(10);
		compassBox.setAlignment(Pos.CENTER);
		Label compassLabel = new Label("Today's Wind");
		Label windDirectionLabel = new Label(currentForecast.get(0).windSpeed);
		windDirectionLabel.setOpacity(5);
		Image compassImage = new Image(getClass().getResourceAsStream("/Compass/compass"+currentForecast.get(0).windDirection+".png"));
		ImageView compass = new ImageView(compassImage);
		compass.setFitWidth(200);
		compass.setFitHeight(200);
		compass.setPreserveRatio(false);
		compass.setSmooth(true);
		compassBox.getChildren().addAll(compassLabel, compass,windDirectionLabel);

		HBox hourlyBox = new HBox(10);
		hourlyBox.setAlignment(Pos.CENTER);
		hourlyBox.setPadding(new Insets(20, 0, 0, 0));

		CategoryAxis xAxis = new CategoryAxis();
		xAxis.setLabel("Hour");
		NumberAxis yAxis = new NumberAxis();
		yAxis.setLabel("Temperature");

		// Create the line chart with x axis as Category and y axis as Number
		LineChart<String, Number> lineChart = new LineChart<>(xAxis, yAxis);
		lineChart.setTitle("Temperature Trend");
		lineChart.setLegendVisible(false);
		lineChart.setCreateSymbols(true); // Show data points

		XYChart.Series<String, Number> series = new XYChart.Series<>();

		SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
		String Date = formatter.format(HourlyForecast.get(0).startTime);
		SimpleDateFormat timeFormatter = new SimpleDateFormat("hh a");
		String currentDate;

		for(Period p : HourlyForecast) {
			currentDate = formatter.format(p.startTime);
			if(!Date.equals(currentDate)) break;
			VBox hourForecast = new VBox(10);
			hourForecast.setAlignment(Pos.CENTER);
			ImageView forecastImage = loadIcon(p.icon);
			Label hourLabel = new Label(timeFormatter.format(p.startTime));
			Label tempLabel = new Label(getTemperature(p.temperature)+"°"+Unit);
			Label description = new Label(p.shortForecast);
			Label WindDir = new Label(p.windDirection);
			Label WindSpeed = new Label(p.windSpeed);
			hourForecast.getChildren().addAll(forecastImage, hourLabel, tempLabel, description,WindDir,WindSpeed);
			hourlyBox.getChildren().add(hourForecast);
			series.getData().add(new XYChart.Data<>(timeFormatter.format(p.startTime), getTemperature(p.temperature)));
		}

		lineChart.getData().add(series);
		// Optionally, set a preferred height for the chart so it remains visible
		lineChart.setPrefHeight(300);

		HBox graphics = new HBox(10,compassBox, lineChart);

		ScrollPane hourlyScrollPane = new ScrollPane(hourlyBox);
		// ScrollPane settings to make it side-scrolling
		hourlyScrollPane.setHbarPolicy(ScrollPane.ScrollBarPolicy.ALWAYS); // Always show horizontal bar
		hourlyScrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.NEVER);  // Never show vertical bar
		hourlyScrollPane.setPannable(true); // Optional: drag to scroll
		// Set preferred size of the ScrollPane
		hourlyScrollPane.setPrefViewportHeight(225);
		hourlyScrollPane.setPrefViewportWidth(400);

		Button backButton = new Button("Back");
		backButton.setOnAction(e -> primaryStage.setScene(mainScene));

		VBox detailedForecastBox = new VBox(10, titleLabel, hourlyLabel, hourlyScrollPane, graphics,backButton);
		detailedForecastBox.setAlignment(Pos.TOP_CENTER);
		detailedForecastBox.setPadding(new Insets(20, 0, 0, 0));

		BorderPane detailedForecastBorder = new BorderPane();
		detailedForecastBorder.setCenter(detailedForecastBox);
		detailedForecastBorder.setPadding(new Insets(10, 20, 10, 20));


		StackPane detailedForecastStack = new StackPane(detailedForecastBorder);
		detailedForecastStack.getStyleClass().add("stack-pane");

		if(Theme == 'A') detailedForecastStack.getChildren().add(0,forecastBackground);

		Scene detailedForecastScene = new Scene(detailedForecastStack,SCENE_WIDTH, SCENE_HEIGHT);

		detailedForecastScene.getStylesheets().clear();
		detailedForecastScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());

		primaryStage.setScene(detailedForecastScene);

	}

	private void showCustomLocationInput() {
		Stage inputStage = new Stage();
		inputStage.setTitle("Enter Custom Location");

		TextField latitudeField = new TextField();
		latitudeField.setPromptText("Enter Latitude");

		TextField longitudeField = new TextField();
		longitudeField.setPromptText("Enter Longitude");

		Button searchButton = new Button("Search");
		searchButton.setStyle("-fx-background-color: rgba(255,255,255,0.25); -fx-font-size: 18px; -fx-padding: 10px 20px;");

		searchButton.setOnAction(event -> {
			try {
				double latitude = Double.parseDouble(latitudeField.getText().trim());
				double longitude = Double.parseDouble(longitudeField.getText().trim());

				if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
					showAlert("Invalid Input", "Latitude must be between -90 and 90, Longitude between -180 and 180.");
					return;
				}

				ArrayList<String> URLs = MyWeatherAPI.getURLs(latitude, longitude);
				if (URLs == null || URLs.isEmpty()) {
					showAlert("Error", "Could not fetch weather data. Please check your latitude and longitude.");
					return;
				}

				String areaData = URLs.get(2);
				currentForecast = MyWeatherAPI.getForecastURL(URLs.get(0));
				HourlyForecast = MyWeatherAPI.getForecastURL(URLs.get(1)); // ✅ FIXED: Ensure hourly forecast is updated

				if (currentForecast == null || currentForecast.isEmpty()) {
					showAlert("Error", "No forecast data available.");
					return;
				}

				if (HourlyForecast == null || HourlyForecast.isEmpty()) {
					showAlert("Error", "No hourly forecast data available.");
					return;
				}

				if(saveToHistory(areaData)) {
					Scanner scanner = new Scanner(areaData);
					scanner.useDelimiter(",");
					String city = scanner.next();
					String state = scanner.next();
					String code = scanner.next();
					int gridX = scanner.nextInt();
					int gridY = scanner.nextInt();
					String newName = city + " (" + state + ")";
					MenuItem newCity = new MenuItem(newName);
					newCity.setOnAction(e -> {
						updateWeather(menuButton, newName, code, gridX, gridY);
					});
					menuButton.getItems().add(newCity);

					fadeBackground(getBackground(currentForecast.get(0).shortForecast));

					menuButton.setText(newName);
					temperature.setText(currentForecast.get(0).temperature + "°" + Unit);
					weather.setText(currentForecast.get(0).shortForecast);
				}
				else{
					showAlert("Error","Location already exists in History");
				}

				inputStage.close();
			} catch (NumberFormatException ex) {
				showAlert("Invalid Input", "Please enter numeric values for latitude and longitude.");
			}
		});

		VBox inputBox = new VBox(10, new Label("Enter Latitude and Longitude"), latitudeField, longitudeField, searchButton);
		inputBox.setAlignment(Pos.CENTER);
		Scene inputScene = new Scene(new StackPane(inputBox), 400, 200);
		inputStage.setScene(inputScene);
		inputStage.show();
	}

	private void showAlert(String title, String message) {
		Alert alert = new Alert(Alert.AlertType.ERROR);
		alert.setTitle(title);
		alert.setHeaderText(null);
		alert.setContentText(message);
		alert.showAndWait();
	}

	public String getBackground(String description){
		description = description.toLowerCase();
		String imageFile = "city.gif";
		if (description.contains("rain")) {
			imageFile = "rain.gif";
		} else if (description.contains("sunny")) {
			imageFile = "sunny.gif";
		} else if (description.contains("cloudy")) {
			imageFile = "cloudy.gif";
		} else if (description.contains("snow")) {
			imageFile = "snow.gif";
		} else if (description.contains("clear")) {
			imageFile = "clear.gif";
		}
		return imageFile;
	}

	public boolean saveToHistory(String areaData) {
		// Define the file to store custom locations
		File file = new File("customLocations.txt");
		try {
			// Create the file if it does not exist
			if (!file.exists()) {
				file.createNewFile();
			}

			// Read all existing lines from the file
			List<String> lines = Files.readAllLines(file.toPath(), StandardCharsets.UTF_8);
			for (String line : lines) {
				// If the line exactly matches the new areaData, mark it as a duplicate
				if (line.trim().equals(areaData.trim())) {
					return false;
				}
			}

			// If the location is not already in the history, append it to the file
			try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {
				writer.write(areaData);
				writer.newLine();
			}
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		return true;
	}

	private void loadCustomLocations() {
		File file = new File("customLocations.txt");
		if (file.exists()) {
			try {
				List<String> lines = Files.readAllLines(file.toPath(), StandardCharsets.UTF_8);
				for (String line : lines) {
					if (!line.trim().isEmpty()) {
						Scanner scanner = new Scanner(line);
						scanner.useDelimiter(",");
						String city = scanner.next();
						String state = scanner.next();
						String code = scanner.next();
						int gridX = scanner.nextInt();
						int gridY = scanner.nextInt();
						scanner.close();

						// Format the menu item label as "City (State)"
						String newName = city + " (" + state + ")";
						MenuItem customCity = new MenuItem(newName);
						customCity.setOnAction(e -> {
							updateWeather(menuButton, newName, code, gridX, gridY);
						});
						menuButton.getItems().add(customCity);
					}
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	public void clearHistory(){

		//Nothing in History, return
		if(menuButton.getItems().size() <= 4){
			showAlert("Error","Nothing saved in History");
			return;
		}
		Stage confirmationStage = new Stage();
		confirmationStage.setTitle("Are you sure?");
		Button yesButton = new Button("Yes");
		Button noButton = new Button("No");

		noButton.setOnAction(e -> confirmationStage.close());
		yesButton.setOnAction(e -> {
			menuButton.getItems().remove(4,menuButton.getItems().size());
			try {
				FileWriter clear = new FileWriter("customLocations.txt");
			}
			catch (IOException e1) {
				e1.printStackTrace();
			}
			confirmationStage.close();
		});
		Label confirmLabel = new Label("Are you sure?");
		HBox answersHbox = new HBox(10,yesButton,noButton);
		answersHbox.setAlignment(Pos.CENTER);
		VBox answersVbox = new VBox(10,confirmLabel,answersHbox);
		answersVbox.setAlignment(Pos.CENTER);

		Scene answersScene = new Scene(new StackPane(answersVbox), 100, 60);
		confirmationStage.setScene(answersScene);
		confirmationStage.show();
	}

	public void detailedDayScene(Stage primaryStage, Period forecast){
		if(forecast == currentForecast.get(0)) {
			showDetailedForecastScene(primaryStage);
			return;
		}

		Image newImage = new Image(getClass().getResourceAsStream("/weather_backgrounds/" + getBackground(forecast.shortForecast)));
		ImageView newForecastBackground = new ImageView(newImage);
		newForecastBackground.setFitWidth(SCENE_WIDTH);
		newForecastBackground.setFitHeight(SCENE_HEIGHT);
		newForecastBackground.setPreserveRatio(false);
		newForecastBackground.setSmooth(true);
		newForecastBackground.setCache(true);

		Label TitleLabel = new Label(menuButton.getText()+ " : " + forecast.name +" Detailed Forecast");
		TitleLabel.setId("TitleLabels");

		Label hourlyLabel = new Label("Hourly Forecast");
		hourlyLabel.setId("SubLabels");

		VBox compassBox = new VBox(10);
		compassBox.setAlignment(Pos.CENTER);
		Label compassLabel = new Label(forecast.name + "'s Wind");
		Label windDirectionLabel = new Label(currentForecast.get(0).windSpeed);
		windDirectionLabel.setOpacity(5);
		Image compassImage = new Image(getClass().getResourceAsStream("/Compass/compass"+currentForecast.get(0).windDirection+".png"));
		ImageView compass = new ImageView(compassImage);
		compass.setFitWidth(200);
		compass.setFitHeight(200);
		compass.setPreserveRatio(false);
		compass.setSmooth(true);
		compassBox.getChildren().addAll(compassLabel, compass,windDirectionLabel);

		HBox hourlyBox = new HBox(10);
		hourlyBox.setAlignment(Pos.CENTER);
		hourlyBox.setPadding(new Insets(20, 0, 0, 0));

		CategoryAxis xAxis = new CategoryAxis();
		xAxis.setLabel("Hour");
		NumberAxis yAxis = new NumberAxis();
		yAxis.setLabel("Temperature");

		// Create the line chart with x axis as Category and y axis as Number
		LineChart<String, Number> lineChart = new LineChart<>(xAxis, yAxis);
		lineChart.setTitle("Temperature Trend");
		lineChart.setLegendVisible(false);
		lineChart.setCreateSymbols(true); // Show data points

		XYChart.Series<String, Number> series = new XYChart.Series<>();

		SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
		String Date = formatter.format(forecast.startTime);
		SimpleDateFormat timeFormatter = new SimpleDateFormat("hh a");
		String currentDate;

		for(Period p : HourlyForecast) {
			currentDate = formatter.format(p.startTime);
			if(!Date.equals(currentDate)) continue;
			VBox hourForecast = new VBox(10);
			hourForecast.setAlignment(Pos.CENTER);
			ImageView forecastImage = loadIcon(p.icon);
			Label hourLabel = new Label(timeFormatter.format(p.startTime));
			Label tempLabel = new Label(getTemperature(p.temperature)+"°"+Unit);
			Label description = new Label(p.shortForecast);
			Label WindDir = new Label(p.windDirection);
			Label WindSpeed = new Label(p.windSpeed);
			hourForecast.getChildren().addAll(forecastImage, hourLabel, tempLabel, description,WindDir,WindSpeed);
			hourlyBox.getChildren().add(hourForecast);
			series.getData().add(new XYChart.Data<>(timeFormatter.format(p.startTime), getTemperature(p.temperature)));
		}

		lineChart.getData().add(series);
		// Optionally, set a preferred height for the chart so it remains visible
		lineChart.setPrefHeight(300);

		HBox graphics = new HBox(10,compassBox, lineChart);

		ScrollPane hourlyScrollPane = new ScrollPane(hourlyBox);
		// ScrollPane settings to make it side-scrolling
		hourlyScrollPane.setHbarPolicy(ScrollPane.ScrollBarPolicy.ALWAYS); // Always show horizontal bar
		hourlyScrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.NEVER);  // Never show vertical bar
		hourlyScrollPane.setPannable(true); // Optional: drag to scroll
		// Set preferred size of the ScrollPane
		hourlyScrollPane.setPrefViewportHeight(225);
		hourlyScrollPane.setPrefViewportWidth(400);

		Button backButton = new Button("Back");
		backButton.setOnAction(e -> primaryStage.setScene(mainScene));

		VBox detailedForecastBox = new VBox(10, TitleLabel, hourlyLabel, hourlyScrollPane, graphics,backButton);
		detailedForecastBox.setAlignment(Pos.TOP_CENTER);
		detailedForecastBox.setPadding(new Insets(20, 0, 0, 0));

		BorderPane detailedForecastBorder = new BorderPane();
		detailedForecastBorder.setCenter(detailedForecastBox);
		detailedForecastBorder.setPadding(new Insets(10, 20, 10, 20));

		StackPane detailedForecastStack = new StackPane(detailedForecastBorder);

		detailedForecastStack.getStyleClass().add("stack-pane");

		if(Theme == 'A') detailedForecastStack.getChildren().add(0,newForecastBackground);

		Scene detailedForecastScene = new Scene(detailedForecastStack,SCENE_WIDTH, SCENE_HEIGHT);

		detailedForecastScene.getStylesheets().clear();
		detailedForecastScene.getStylesheets().add(getClass().getResource("cssThemes/Theme" + currentTheme + ".css").toExternalForm());

		primaryStage.setScene(detailedForecastScene);
	}
}
