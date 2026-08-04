import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, get_sun
import astropy.units as u

EARTH_RADIUS = 6371.0  # km

def is_in_earth_shadow(lat, lon, alt_km, timestamp):
    """
    Returns 1 if the satellite is in Earth's shadow at the given location and altiude, 0 otherwise.

    Projects the satellite-to-Sun ray onto the Earth-Sun line and checks
    whether the closest approach to Earth's center falls within Earth's radius
    (6371 km sphere). Positions computed in ITRS coordinates via astropy.

    Parameters
    ----------
    lat : float
        Geodetic latitude in degrees.
    lon : float
        Geodetic longitude in degrees.
    alt_km : float
        Altitude above Earth's surface in kilometers.
    timestamp : str or datetime-like
        Any time format accepted by astropy.time.Time.
    """

    # Convert to astropy EarthLocation
    location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=alt_km*u.km)
    
    # Get Sun position in ITRS (ECEF) coordinates
    t = Time(timestamp)
    sun_itrs = get_sun(t).transform_to('itrs')
    sun_vector = np.array([sun_itrs.x.to(u.km).value,
                           sun_itrs.y.to(u.km).value,
                           sun_itrs.z.to(u.km).value])
    
    # Satellite position in ECEF
    sat_vector = np.array([location.x.to(u.km).value,
                           location.y.to(u.km).value,
                           location.z.to(u.km).value])
    
    # Vector from satellite to Sun
    sat_to_sun = sun_vector - sat_vector
    
    # Project satellite position onto Sun vector
    t_proj = -np.dot(sat_vector, sat_to_sun) / np.dot(sat_to_sun, sat_to_sun)
    
    if t_proj < 0:
        return False  # Sun is "behind" satellite
    
    # Closest approach distance from Earth's center to Sun-satellite line
    closest_dist = np.linalg.norm(sat_vector + t_proj * sat_to_sun)
    
    return (closest_dist < EARTH_RADIUS).astype(int)



if __name__ == "__main__":
    import pandas as pd
    clean_rad = pd.read_excel("clean_data_kp.xlsx")

    clean_rad['alt0'] = 0

    clean_rad["ground_shadow"] = clean_rad.apply(
        lambda row: is_in_earth_shadow(
            row["lat"],
            row["lon"],
            row["alt0"],
            row["timestamp"]
        ),
        axis=1
    ).replace({True: 1, False: 0})

    clean_rad.drop("alt0", axis=1, inplace=True)
    print(clean_rad.head())