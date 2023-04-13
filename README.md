# BrazilFlights

BrazilFlights is an application that creates a graph of selected flights using the networkx library

## Filters

On the main function you can pass 4 attributes to make the flights graph

### date_range

On this attribute you can pass a date range, following this pattern '2023-01-01/2023-01-02', to get all flights on this range

```python
__main__(date_range = '2023-04-10/2023-04-10')
```

### departure_hour_range

If you pass only one day to the attribute date_range ('2023-04-10/2023-04-10'), you can select the range of flights departure hour following this pattern '00:00-23:59'

```python
__main__(date_range = '2023-01-01/2023-01-01', departure_hour_range = '10:00-11:00')
```

### code_state

On this attribute you can pass an array of brazilian states (UF), following this pattern ['SP', 'MG'], to get all flights between that states

```python
__main__(date_range = '2023-01-01/2023-01-01', code_state= ['SP','MG'])
```

### transport_object

This attribute can filter the passenger flights if you pass 'PASSAGEIROS' and cargo flights if you pass 'CARGA', by default this get both flights types

```python
__main__(date_range = '2023-01-01/2023-01-01', transport_object = 'CARGA')
```

## Examples

