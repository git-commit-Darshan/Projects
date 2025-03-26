package weather;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.Date;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Period{
    public int number;
    public String name;
    public Date startTime;
    public Date endTime;
    public boolean isDaytime;
    public int temperature;
    public String temperatureUnit;
    public String temperatureTrend;
    public ProbabilityOfPrecipitation probabilityOfPrecipitation;
    public String windSpeed;
    public String windDirection;
    public String icon;
    public String shortForecast;
    public String detailedForecast;
}
