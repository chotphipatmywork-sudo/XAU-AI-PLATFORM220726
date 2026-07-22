//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : VolatilityConfig.mqh                                   |
//| Layer   : Brain / Volatility / Config                            |
//| Version : 1.1.0                                                  |
//| Purpose : Configuration for Volatility Package                   |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_CONFIG_VOLATILITYCONFIG_MQH
#define CORE_BRAIN_VOLATILITY_CONFIG_VOLATILITYCONFIG_MQH

//--------------------------------------------------
// Volatility Configuration
//--------------------------------------------------

class CVolatilityConfig
{
public:
    int ATRPeriod;

    int ADRPeriod;

    int AIRegimeLookback;

    CVolatilityConfig()
    {
        ATRPeriod = 14;
        ADRPeriod = 20;

        AIRegimeLookback = 16;
    }
};

#endif
