# BrazilFlights

BrazilFlights is an application that creates a graph of selected flights using the networkx library

## Filters

On the main function you can pass 4 parameters to make the flights graph

### date_range

On this parameter you can pass a date range, following this pattern '2023-01-01/2023-01-02', to get all flights on this range

```python
__main__(date_range = '2023-01-01/2023-01-02')
```

### departure_hour_range

If you pass only one day to the parameter date_range ('2023-01-01/2023-01-01'), you can select the range of flights departure hour following this pattern '00:00-23:59'

```python
__main__(date_range = '2023-01-01/2023-01-01', departure_hour_range = '10:00-11:00')
```

### code_state

On this parameter you can pass an array of brazilian states (UF), following this pattern ['SP', 'MG'], to get all flights between that states

```python
__main__(date_range = '2023-01-01/2023-01-01', code_state= ['SP','MG'])
```

### transport_object

This parameter can filter the passenger flights if you pass 'PASSAGEIROS' and cargo flights if you pass 'CARGA', by default this get both flights types

```python
__main__(date_range = '2023-01-01/2023-01-01', transport_object = 'CARGA')
```

## Examples

### date_range = '2023-01-01/2023-01-01', departure_hour_range = '10:00-11:00'

![Figure_1](https://user-images.githubusercontent.com/55093266/231880913-13162aae-f9f7-483a-8b48-b30f3a715e67.png)
