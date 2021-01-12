# Raspberry PI : DC voltage measurement

## Preamble

The Raspberry PI is a small, single-board computer that runs
under Raspberry-OS (distribution of Debian). The PI offers a complete 
digital inputs-outputs bus, but no analog input.

The goal of my project is to allow the monitoring of the state of charge of the
battery from uninterruptible power supply to ensure a clean shutdown
system in the event of a power failure. The LIPO battery I use
sees its voltage vary from 4.2 to 3.5 V.

## Introduction

For a project on Raspberry PI I must ensure an uninterruptible power supply
in the event of a drop in the electrical network. I found solutions at different
suppliers to properly ensure the transition between network and
battery but these systems do not allow the PI to be informed that the battery is
soon empty and the operating system should be shut down properly.

For this purpose I have developed and tested several variants all based
on the same principle: measure the time taken by a capacitor to
charge to a known voltage and convert this time to a value of
voltage. These different tests led me to the solution that I
offers today.

## Basic principle

*Insert the schematic*

The voltage to be measured is applied to the BBU-BAT input. The command
RPI-CMD is connected to the GPIO terminal (8 in my case) of the PI set as
an output and the RPI-MES output is connected to the GPIO terminal (10 in
my case) of the PI set as an entry. The VCC Connections (terminal 4) and
GND (terminal 6) are connected to the PI. The mass (GND) of the signal to be 
measured and that of the PI are linked.

The principle of operation is as follows:

Before launching a measurement the RPI-CMD output is set to "1" thus the MOSFET T1
is made conductive which discharges the capacitor C1. To start the measurement, the 
PI puts the input CMD at "0" so the MOSFET T1 is blocked and the capacitor can be 
charged through the resistor R1 supplied by the voltage to be measured. When the 
voltage at capacitor terminals reach 2.5V, comparator IC1 passes its
output from "1" to "0". The PI measures the time elapsed between the launch
of the measurement and the moment when the comparator output goes from "1" to
"0". Knowing the characteristics of the circuit R1, C1 it is
possible to claculate the value of the voltage applied to the input
BBU-BAT by the formula:

*Insert équation*

Where UTRIG = reference voltage (2.5V) and TMES = time elapsed between
start of the measurement and the moment when the comparator output changes from
“1” to “0” minus the latency time.

## System calibration

The detection of the change of state of the RPI-MES entry is managed in Python
using an interrupt which implies taking into account the time
PI latency (time that the PI takes to respond to the interrupt).
This time can be measured simply by connecting the RPI-CMD (8) output to
the RPI-MES input (10) and measures the time elapsed between the change
status of the output and the reaction of the PI.

## Limits of the principle used

#### Current consumed at the measuring point

By connecting the input without amplifier directly to the point to
measuring current is necessarily consumed on this source. As
the resistance value is 100kΩ, the maximum current drawn from the
measurement is 100 μA. It is up to the user to determine if this is
acceptable. In my case no problem because I measure the voltage of the
battery from the uninterruptible power supply.

#### Permissible voltage range

The principle used does not allow a voltage measured below 2.8V
to ensure that the voltage across the capacitor can reach
2.8V and switch the comparator output. The maximum voltage that
can be applied is limited by the LM393 comparator and can
reach 36V. However, as there is no protection between the entrance
measurement and the PI, a fault in the LM393 could cause the voltage
input directly to the RPI-MES terminal or, if the MOSFET becomes
defective, on the RPI-CMD terminal. I therefore recommend not to exceed
the maximum voltage admissible by the GPIO port of the PI is 5V.

## Measurement reliability

The measurement principle depends very strongly on the latency time of the PI.
If the processor is busy with other priority tasks, the
latency can increase sharply over one or two measures. To eliminate
these bad measurements I make a large number of measurements and reject
those which are outside 1.5 standard deviations of all the measurements
then I average the remaining measurements.

## Software

The software is written in Python and can be downloaded from GitHub
by the link: <https://github.com/josmet52/pidcmes>

## Nomenclature

The components used are:

- T1 = BS170 - MOSFET channel N
- D1 = LM336-2.5V - 2.5V reference diode
- IC1 = LM393N - Low-Offset Voltage, Dual Comparators
- R1 = 100kΩ - Resistance
- R2 = 2.5kΩ - Resistance
- C1 = 1μF - Ceramic capacitor