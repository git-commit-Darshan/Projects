package weather;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
@JsonIgnoreProperties(ignoreUnknown = true)

public class Root2 {
    public String type;
    public Geometry2 geometry;
    public Properties properties;

    }

