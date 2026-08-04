import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from shapely.geometry import Point


def satellite_path(df: pd.Series | pd.DataFrame, ax: Axes | None = None):
    '''
    Plots the path of a satellite given a pandas dataframe with columns "lat", "lon", and "timestamp"
    '''

    #Save if ax was originally None for the if statement at the end of the function
    original_ax = ax

    #If ax is none (in the case that this will not be part of a subplot) create a new fig and ax
    if ax == None:
        fig, ax = plt.subplots(figsize=(14, 9))
    #Otherwise, get the figure from the subplot
    else:
        fig = ax.get_figure()

    #Load a world map
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url)
    
    #Save lat and lon columns as a Point object and turn df into a geopandas dataframe
    geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]        
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    #Plot world and satellite path
    world.plot(ax=ax, color="lightgrey")
    gdf.plot(ax=ax, color="black")

    #Make sure the figure does not get warped
    ax.set_aspect("equal", adjustable="box")

    #If this is not a part of a subplot, show the plot
    if original_ax == None:
        #Title the plot
        ax.set_title(f"Satellite path from {df.iloc[0]["timestamp"]} to {df.iloc[-1]["timestamp"]}")
        plt.show()
        return
    #If it is a part of a subplot, return the Axes object
    else:
        #Title the plot
        ax.set_title("Satellite Path")
        return ax


def group_particles(df: pd.Series | pd.DataFrame, ax: Axes | None = None):
    '''
    Plot readings for "proton0_ps", "electron0_ps", and "xray0_ps" for a supplied subset of the data
    '''

    #Save if ax was originally None for the if statement at the end of the function
    original_ax = ax

    #If ax is none (in the case that this will not be part of a subplot) create a new fig and ax
    if ax == None:
        fig, ax = plt.subplots(figsize=(14, 9))
    else:
    #Otherwise, get the figure from the subplot
        fig = ax.get_figure()

    #Plot "proton0_ps", "electron0_ps", and "xray0_ps" columns on the same axis
    #There is a square-root-scaled y-axis to compress the scale without removing 0s
    ax.plot(df["timestamp"], np.sqrt(df["proton0_ps"]), color="black", marker="o", label="proton0 per sec", alpha=0.75)
    ax.plot(df["timestamp"], np.sqrt(df["electron0_ps"]), color="lightblue", marker="o", label="electron0 per sec", alpha=0.75)
    ax.plot(df["timestamp"], np.sqrt(df["xray0_ps"]), color="green", marker="o", label="xray0 per sec", alpha=0.75)

    #Move the y-axis label to the right of the graph and name the axis
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Particle Counts Per Second (Sqrt Scale)")
    
    #Title the plot
    ax.set_title("Particle Counts Per Second")
    
    #Only show a few timestamps on the x-axis for readability
    ax.xaxis.set_major_locator(ticker.LinearLocator(numticks=6))
    date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S') 
    ax.xaxis.set_major_formatter(date_format)
    
    #If this is not a part of a subplot, show the plot
    if original_ax == None:
        #Position legend whever matplotlib thinks is best
        fig.legend()
        plt.show()
        return
    #If it is a part of a subplot, return the Axes object
    else:
        #Position legend to the right of the satellite path.
        fig.legend(loc = (0.83, 0.325))
        return ax


def particles_path(df: pd.Series | pd.DataFrame):
    '''
    Given a subset of a pandas dataframe of RadStar data, create a subplot that calls both satellite_path() and group_particles()
    group_particles() will be on the top with the legend to the right of satellite_path()
    '''
    #Create subplot
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(14,9))

    #Add two graphs to the subplot
    ax = group_particles(df, ax)
    ax2 = satellite_path(df, ax2)

    #Add a title
    fig.suptitle(f"Particle counts and satellite path from {df.iloc[0]["timestamp"]} to {df.iloc[-1]["timestamp"]}", fontsize="xx-large")

    #Show the plot and return
    plt.show()
    return



if __name__ == "__main__":
    #Load data
    test = pd.read_excel("clean_data_kp.xlsx")
    test = test[test["group"] == 1]
    
    #Run all three functions for testing purposes
    satellite_path(test)
    group_particles(test)
    particles_path(test)
