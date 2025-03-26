package weather;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.ArrayList;
import java.util.Date;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Properties{
    public String units;
    public String forecastGenerator;
    public Date generatedAt;
    public Date updateTime;
    public String validTimes;
    public Elevation elevation;
    public String forecastHourly;
    public String forecast;
    public String gridId;
    public int gridX;
    public int gridY;
    public ArrayList<Period> periods;
    public RelativeLocation relativeLocation;
    public String city;
    public String state;
}
