no_no_addrs = [
    0x000B7EE4, # alt up movement
    0X000B7E44, # uncontrollable left movement
]

# TODO(Lazy) This list assume bifurcated nops
# Finding the actual problem adders and moving them into no_no_addrs would be best
all_no_no_indices = [
    -2462,
    -2423,
    -2422,
    -2421,
    -2420,
    -2419,
    -2418,
    -2417,
    -2416,
    -2415,
    -2414,
    -2413,
    -2412,
    -2411,
    -2410,
    -2409,
    -2408,
    -2407,
    -2406,
    -2405,
    -2404,
    -2403,
    -2402,
    -2401,
    -2400,
    -2399,
    -2398,
    -2397,
    -2396,
    -2395,
    -2394,
    -2393,
    -2392,
    -2391,
    -2390,
    -2389,
    -2388,
    -2387,
    -2386,
    -2385,
    -2384,
    -2383,
    -2382,
    -2381,
    -2380,
    -2379,
    -2378,
    -2377,
    -2376,
    -2375,
    -2374,
    -2373,
    -2372,
    -2371,
    -2370,
    -2369,
    -2368,
    -2367,
    -2366,
    -2365,
    -2364,
    -2363,
    -2362,
    -2361,
    -2360,
    -2359,
    -2358,
    -2357,
    -2356,
    -2355,
    -2354,
    -2353,
    -2352,
    -2351,
    -2350,
    -2349,
    -2348,
    -2347,
    -2346,
    -2345,
    -2344,
    -2343,
    -2342,
    -2341,
    -2340,
    -2339,
    -2338,
    -2337,
    -2336,
    -2335,
    -2334,
    -2333,
    -2332,
    -2331,
    -2330,
    -2329,
    -2328,
    -2327,
    -2326,
    -2325,
    -2324,
    -2323,
    -2322,
    -2321,
    -2320,
    -2319,
    -2318,
    -2317,
    -2316,
    -2315,
    -2314,
    -2313,
    -2312,
    -2311,
    -2310,
    -2309,
    -2308,
    -2307,
    -2306,
    -2305,
    -2304,
    -2303,
    -2302,
    -2301,
    -2300,
    -2299,
    -2298,
    -2297,
    -2296,
    -2295,
    -2294,
    -2293,
    -2292,
    -2291,
    -2290,
    -2289,
    -2288,
    -2287,
    -2286,
    -2285,
    -2284,
    -2283,
    -2282,
    -2281,
    -2280,
    -2279,
    -2278,
    -2277,
    -2276,
    -2275,
    -2274,
    -2273,
    -2272,
    -2271,
    -2270,
    -2269,
    -2268,
    -2267,
    -2266,
    -2265,
    -2264,
    -2263,
    -2262,
    -2261,
    -2260,
    -2259,
    -2258,
    -2257,
    -2256,
    -2255,
    -2254,
    -2253,
    -2252,
    -2251,
    -2250,
    -2249,
    -2248,
    -2247,
    -2246,
    -2245,
    -2244,
    -2243,
    -2242,
    -2241,
    -2240,
    -2239,
    -2238,
    -2237,
    -2236,
    -2235,
    -2234,
    -2233,
    -2232,
    -2231,
    -2230,
    -2229,
    -2228,
    -2227,
    -2226,
    -2225,
    -2224,
    -2223,
    -2222,
    -2221,
    -2220,
    -2219,
    -2218,
    -2217,
    -2216,
    -2215,
    -2214,
    -2213,
    -2212,
    -2211,
    -2210,
    -2209,
    -2208,
    -2207,
    -2206,
    -2205,
    -2204,
    -2203,
    -2202,
    -2201,
    -2200,
    -2199,
    -2198,
    -2197,
    -2196,
    -2195,
    -2194,
    -2193,
    -2192,
    -2191,
    -2190,
    -2189,
    -2188,
    -2187,
    -2186,
    -2185,
    -2184,
    -2183,
    -2182,
    -2181,
    -2180,
    -2179,
    -2178,
    -2177,
    -2176,
    -2175,
    -2174,
    -2173,
    -2172,
    -2171,
    -2170,
    -2169,
    -2168,
    -2167,
    -2166,
    -2165,
    -2164,
    -2163,
    -2162,
    -2161,
    -2160,
    -2159,
    -2158,
    -2157,
    -2156,
    -2155,
    -2154,
    -2153,
    -2152,
    -2151,
    -2150,
    -2149,
    -2148,
    -2147,
    -2146,
    -2145,
    -2144,
    -2143,
    -2142,
    -2141,
    -2140,
    -2139,
    -2138,
    -2137,
    -2136,
    -2135,
    -2134,
    -2133,
    -2132,
    -2131,
    -2130,
    -2129,
    -2128,
    -2127,
    -2126,
    -2125,
    -2124,
    -2123,
    -2122,
    -2121,
    -2120,
    -2119,
    -2118,
    -2117,
    -2116,
    -2115,
    -2114,
    -2113,
    -2107,
    -2102,
    -2101,
    -2100,
    -2099,
    -2098,
    -2097,
    -2096,
    -2095,
    -2013,
    -1672,
    -1666,
    -1658,
    -1634,
    -1578,
    -1527,
    -1525,
    -1434,
    -1402,
    -1385,
    -1366,
    -1358,
    -1355,
    -1335,
    -1326,
    -1319,
    -1317,
    -1306,
    -1300,
    -1265,
    -1221,
    -1210,
    -1198,
    -1195,
    -1141,
    -1137,
    -1125,
    -1065,
    -1064,
    -1054,
    -1047,
    -1045,
    -1032,
    -1005,
    -1004,
    -997,
    -996,
    -993,
    -981,
    -949,
    -943,
    -938,
    -719,
    -391,
    -372,
    -312,
    -309,
    -297,
    -261,
    -255,
    -248,
    -245,
    -242,
    -236,
    -235,
    -234,
    -232,
    -226,
    -222,
    -219,
    -218,
    -217,
    -214,
    -213,
    -212,
    -211,
    -208,
    -192,
    -189,
    -188,
    -185,
    -182,
    -180,
    -178,
    -168,
    -164,
    -162,
    -160,
    -158,
    -154,
    -151,
    -135,
    -117,
    -115,
    -111,
    -108,
    -107,
    -104,
    -84,
    -62,
    335,
    336,
    337,
    341,
    344,
    346,
    347,
    353,
    354,
    355,
    357,
    358,
    359,
    363,
    366,
    367,
    369,
    370,
    372,
    373,
    453,
    468,
]


hira_no_no_indices = [
    -1,  # destroys the linked list that displays the letter and runs the code
    #26,  # liable to have their movement information screwed up by a needed 0x30 byte (could be worked around in the future)
    #34,  # liable to have their movement information screwed up
    #64,  # liable to have their movement information screwed up
    #68,  # this is also the exit? # liable to have their movement information screwed up
    #74,  # liable to have their movement information screwed up
    #94,  # liable to have their movement information screwed up


    109, # breaks payload execution?
    110, # has it's movement info broken on the way to 0x38
    25, # breaks linked list/payload execution
    26, # -16 screws up its movement
    -126, # -33 screw up its movement
    84, # breaks payload execution since characters aren't rendered
    59, # breaks linked list/payload execution
    -14, # 47 has its movement screwed up
    -4, # breaks movement for 154
    -9, # breaks movement for 104
    -13, # breaks movement for 64
    -22, # screws up movement for 94

    -39, # breaks kata -265
    -27, # breaks kata -145

    74, # inserting (selecting with "o") at -12 breaks movement at 74

    #10,# TODO(Lazy) why does this appear to break linked list? It should be fine

    #154, # ?
    #-157, # missed terminal subgraph?
    #-126, # ?

    -109, # breaks credits, kinda?
]
hira_no_no_indices.extend(all_no_no_indices)

kata_no_no_indices = [
     25, # ?
    -43, # ?
    -69, # ?
     59, # breaks LL
    -80, # causes the first 0x30 bytes to be rewritten on insert (may want to look into this later...)
    -85, # causes frame drops in Bizhawk?

    -105, # breaks inserts?
    -106, # breaks inserts?
]
kata_no_no_indices.extend(all_no_no_indices)

latin_no_no_indices = [
        26,  # liable to have their movement information screwed up
        36,  # liable to have their movement information screwed up
        68,  # liable to have their movement information screwed up
        152,  # ?
        153,  # ?

        25, # destroys the linked list that displays the letters and runs the code
        67, # destroys something that causes the code not to be run

        182, # noops out own code ?

        -284,
        -1071,

        # testing to avoid credits crash
        #-114,
        #-115,
        #-116,
        #-34,
        #-31,
]
latin_no_no_indices.extend(all_no_no_indices)

hira_most_no_no_indices = [-1, -109]
hira_most_no_no_indices.extend(all_no_no_indices)

hira_all_no_no_indices = []
hira_all_no_no_indices.extend(all_no_no_indices)