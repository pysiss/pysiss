# PySISS OGCServiceMapping specification

Because we have several OGC versions to support, we define a mapping between These interfaces use a modified pseudo-JSON syntax to specify how to fill out requests for OGC services. They mean you can use a single parameter to fill out a variety of requests (an example of the differences: WCS1.0 uses `ident` to refer to a given coverage, while WCS1.1 uses `coverage` - our mapping means we can use `'@ident'` for both).

Requests are constructed by the OGCServiceMapping object when the request method is called with a set of keyword arguments. These keywords are used to replace variables prefixed with an @ in the parameters.json files. Then all the parameters are serialized into a Get request in `?...&<parameter_name>=<value>&...` format.

The basic outline is as follows:


```json
{
    "request1": {
        <parameter_name>: <parameter_spec>,
        <parameter_name>: <parameter_spec>,
        <parameter_name>: <alternative_parameter_spec>
    }
    "request2": {
        <parameter_name>: <parameter_spec>
    }
}
```

A `<parameter_name>` is a string. If the string begins with a question mark (e.g. `?bbox`) then it is an optional parameter and will only be included in the request if the relevant parameters are provided. If there is no question mark then the parameter is required, and a ValueError will be raised if it isn't provided to the request.

A `<parameter_spec>` can either be

1. a plain string, in which case it is assumed to be constant for all requests (e.g. `"request": "getcapabilities"`), or

2. a string beginning with an `@` character, in which case it is filled in from the keyword arguments supplied to the query constructor (e.g. `"coverage": "@ident"` will become `"coverage": "3dfts-425ks"` if `ident='3dfts-425ks'` is passed in the keywords), or

3. a dictionary containing a Python string template, and a list of substitutions to construct the string. For example,
```json
"subset": {
    "string": "ogc:longitude({low},{high})",
    "low": "@minlongitude",
    "high": "@maxlongitude"
}
```
becomes `"subset": "ogc:longitude(10,20)"` if `minlongitude=10, maxlongitude=20` is passed to the query constructor.

Keys and parameters which are not specified in the keywords are removed from the request, so the 'subset' example given above won't be present in the final request if one of `maxlongitude` or `minlongitude` are missing.

These files use a JSON-esqe syntax - the only difference is that dictionary keys are not required to be unique, so you can do something like

```json
"getcoverage": {
    ...
    "?bbox": {
        "string": "{minlongitude},{minlatitude},{maxlongitude},{maxlatitude}",
        "minlongitude": "@minlongitude",
        "maxlongitude": "@maxlongitude",
        "minlatitude": "@minlatitude",
        "maxlatitude": "@maxlatitude"
    },
    "?bbox": {
        "string": "{longitude},{minlatitude},{longitude},{maxlatitude}",
        "longitude": "@longitude",
        "minlatitude": "@minlatitude",
        "maxlatitude": "@maxlatitude"
    },
    "?bbox": {
        "string": "{longitude},{latitude},{longitude},{latitude}",
        "longitude": "@longitude",
        "latitude": "@latitude"
    },
    ...
}
```

so that only the one with all the parameters specified will actually be used. If more than one of these is filled then they will all be included in the request. So for example, when doing WCS calls using the 2.0 KVP protocol, you need to have multiple `subset` clauses, each one relating to a seperate dimension. You can specify this using the following:

```json
"getcoverage": {
    ...
    "?subset": {
        "string": "ogc:longitude({point})",
        "point": "@longitude"
    },
    "?subset": {
        "string": "ogc:latitude({point})",
        "point": "@latitude"
    },
    "?subset": {
        "string": "ogc:phenomenon-time({point})",
        "point": "@time"
    }
    ...
}
```
which picks out a single pixel at `(@longitude, @latitude, @time)`.

**Folder heirarchy**

Interface folders are stored in the following heirarchy

    interfaces > service_name > version_string > {specfiles}

where `service_name` is an OGC service string like 'wcs', 'csw', 'wfs', and `version_string` is an OGC version number.

**Getting parameters**

The script `get_parameters.py` in this folder can be used to get a list of all the parameters defined for a particular services, so you can make sure that your class uses all of them!
