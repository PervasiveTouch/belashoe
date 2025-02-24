#include <Bela.h>
#include <libraries/Trill/Trill.h>
#include <libraries/Gui/Gui.h>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <sys/time.h>
#include "circularbuffer.h"

#define NUM_CAP_CHANNELS 8
#define BUFFER_SIZE 500
#define LOGGING_INTERVAL 5000   // Interval in microseconds

Trill touchSensor;
Gui gui;

std::ofstream file;

CircularBuffer sensorBuffers[NUM_CAP_CHANNELS] = {
	CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE), 
	CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE), CircularBuffer(BUFFER_SIZE)
};

// Sleep time for auxiliary task
unsigned int gTaskSleepTime = 1400; // microseconds -> according to the scan time at normal speed and 13 bits
// Time period (in seconds) after which data will be sent to the GUI
float gTimePeriod = 0.1;

// Readings for all the different pads on the Trill Craft
struct LogEntry{
    timeval tv;
    float gSensorReading[NUM_CAP_CHANNELS] = { 0.0 };
};

std::vector<LogEntry> dataBuffer;

void writeBufferToCSV(){
	if (!file.is_open())
    {
        const std::string filename = "data.csv";
        file.open(filename, std::ios::app); // Open file in append mode
        if (!file.is_open())
        {
            std::cerr << "Unable to open file: " << filename << std::endl;
            return;
        }
    }
    
    for (const auto& entry : dataBuffer) {
        file << entry.tv.tv_sec << "," << entry.tv.tv_usec;
        for (float value : entry.gSensorReading) {
            file << "," << value;
        }
        file << "\n";  // Newline for next entry
    }

    file.close();
    std::cout << "Saved " << dataBuffer.size() << " entries" << std::endl;
}

void logTouchInputToBuffer(std::vector<float> input)
{
	LogEntry currentReading;
	
    // Add a timestamp
    gettimeofday(&currentReading.tv, NULL);

	for(unsigned int i = 0; i < NUM_CAP_CHANNELS; i++)
		currentReading.gSensorReading[i] = input[i];
	
    dataBuffer.push_back(currentReading);

    // std::cout << "Time difference: " << currentReading.tv.tv_sec - tv.tv_sec << " - " << currentReading.tv.tv_usec - tv.tv_usec << "\n";
}

void closeCSVFile()
{
    if (file.is_open())
    {
        file.close();
    }
}

void readFromSensor(void *)
{
    while(!Bela_stopRequested())
	{
		// Read raw data from sensor
		touchSensor.readI2C();
		usleep(gTaskSleepTime);
	}
}

void writeLog(void *)
{
    while(!Bela_stopRequested())
	{
		writeBufferToCSV();
        dataBuffer.clear();  // Clear buffer after writing
        usleep(1000000);
	}
}

void loopLogging(void *)
{
    while(!Bela_stopRequested())
    {
        logTouchInputToBuffer(touchSensor.rawData);
        for (int i = 0; i < NUM_CAP_CHANNELS; i++) {
			sensorBuffers[i].push_back(touchSensor.rawData[i]);
		}
        usleep(LOGGING_INTERVAL);
    }
}

bool setup(BelaContext *context, void *userData)
{
    // Setup a Trill Craft on i2c bus 1, using the default address.
    if (touchSensor.setup(1, Trill::CRAFT) != 0)
    {
        fprintf(stderr, "Unable to initialise Trill Craft\n");
        return false;
    }
    touchSensor.printDetails();

    touchSensor.setMode(Trill::DIFF);   // set the sensor to DIFF mode
    touchSensor.setScanSettings(2, 13); // 2 = normal update speed, 13 bit resolution -> 1400us scan time
    touchSensor.setPrescaler(3);

    gui.setup(context->projectName);

    Bela_runAuxiliaryTask(readFromSensor);
    Bela_runAuxiliaryTask(writeLog);
    Bela_runAuxiliaryTask(loopLogging);

    return true;
}

void render(BelaContext *context, void *userData)
{
    static unsigned int count = 0;

	for(unsigned int n = 0; n < context->audioFrames; n++) {
		// Send number of touches, touch location and size to the GUI
		// after some time has elapsed.
		if(count >= gTimePeriod*context->audioSampleRate)
		{
			// Send rawData to the GUI
			gui.sendBuffer(0, touchSensor.rawData); // Channel 0
			float max_values[NUM_CAP_CHANNELS];
			for (int i = 0; i < NUM_CAP_CHANNELS; i++) {
				max_values[i] = sensorBuffers[i].getMax();	
			}
			gui.sendBuffer(1, max_values);
			count = 0;
		}
		count++;
	}
}

void cleanup(BelaContext *context, void *userData)
{
	closeCSVFile();
}