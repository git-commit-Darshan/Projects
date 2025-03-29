import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import weather.Period;
import weather.Properties;
import weather.Root;
import weather.Root2;
import weather.WeatherAPI;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;

public class MyWeatherAPI extends WeatherAPI {



    public static ArrayList<Period> getForecastHourly(String region, int gridx, int gridy) {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.weather.gov/gridpoints/"+region+"/"+String.valueOf(gridx)+","+String.valueOf(gridy)+"/forecast/hourly"))
                //.method("GET", HttpRequest.BodyPublishers.noBody())
                .build();
        HttpResponse<String> response = null;
        try {
            response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        } catch (Exception e) {
            e.printStackTrace();
        }
        Root r = getObject(response.body());
        if(r == null){
            System.err.println("Failed to parse JSon");
            return null;
        }
        return r.properties.periods;
    }

    public static ArrayList<String> getURLs(double lat, double lon) {
        // Round latitude and longitude to 4 decimal places
        lat = Math.round(lat * 10000.0) / 10000.0;
        lon = Math.round(lon * 10000.0) / 10000.0;


        System.out.println("Rounded Coordinates: lat=" + lat + ", lon=" + lon);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.weather.gov/points/" + lat + "," + lon))
                .build();
        HttpResponse<String> response = null;
        try {
            response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("API Response: " + response.body()); // Debugging line
        } catch (Exception e) {
            e.printStackTrace();
        }

        Root2 r = getObject2(response.body());

        if (r == null || r.properties == null) {
            System.err.println("Failed to parse JSON or API response is incomplete: " + response.body());
            return null;
        }

        ArrayList<String> URLs = new ArrayList<>();
        if (r.properties.forecast != null) {
            URLs.add(r.properties.forecast);
            System.out.println("Daily Forecast URL: " + r.properties.forecast);
        } else {
            System.err.println("Missing daily forecast URL");
        }

        if (r.properties.forecastHourly != null) {
            URLs.add(r.properties.forecastHourly);
            System.out.println("Hourly Forecast URL: " + r.properties.forecastHourly);
        } else {
            System.err.println("Missing hourly forecast URL");
        }

        URLs.add(r.properties.relativeLocation.properties.city+","+r.properties.relativeLocation.properties.state+","+r.properties.gridId+","+r.properties.gridX+","+r.properties.gridY);

        return URLs;
    }

    public static ArrayList<Period> getForecastURL(String URL) {
        if (URL == null) {
            System.err.println("Forecast URL is null");
            return null;
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(URL))
                .build();
        HttpResponse<String> response = null;
        try {
            response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("Fetching forecast data from: " + URL);
            System.out.println("Response: " + response.body()); // Debugging line
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }

        Root r = getObject(response.body());
        if (r == null || r.properties == null) {
            System.err.println("Failed to parse JSON for forecast");
            return null;
        }

        return r.properties.periods;
    }

    public static Root2 getObject2(String json) {
        ObjectMapper om = new ObjectMapper();
        try {
            return om.readValue(json, Root2.class);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static Root getObject(String json) {
        ObjectMapper om = new ObjectMapper();
        try {
            return om.readValue(json, Root.class);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        return null;
    }
}
