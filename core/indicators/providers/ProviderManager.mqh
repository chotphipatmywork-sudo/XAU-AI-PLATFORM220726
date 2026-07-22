//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ProviderManager.mqh                                    |
//| Layer   : Indicators / Providers                                 |
//| Version : 1.2.0                                                  |
//| Purpose : Central Manager for Indicator Providers                |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_PROVIDERS_PROVIDERMANAGER_MQH
#define CORE_INDICATORS_PROVIDERS_PROVIDERMANAGER_MQH

#include "../models/IndicatorContext.mqh"

#include "EMAProvider.mqh"
#include "ATRProvider.mqh"

//--------------------------------------------------
// Provider Manager
//--------------------------------------------------

class CProviderManager
{
private:
    CIndicatorContext m_context;

    CEMAProvider m_emaProvider;
    CATRProvider m_atrProvider;

public:
    //--------------------------------------------------
    // Constructor
    //--------------------------------------------------

    CProviderManager()
    {
    }

    //--------------------------------------------------
    // Context
    //--------------------------------------------------

    void SetContext(const CIndicatorContext &context)
    {
        m_context = context;

        m_emaProvider.SetContext(context);
        m_atrProvider.SetContext(context);
    }

    //--------------------------------------------------
    // Update
    //--------------------------------------------------

    bool Update()
    {
        bool emaOK = m_emaProvider.Update();
        bool atrOK = m_atrProvider.Update();

        return (emaOK && atrOK);
    }

    //--------------------------------------------------
    // EMA Interface
    //--------------------------------------------------

    double GetEMA(
        const int period,
        const int shift = 0)
    {
        return m_emaProvider.GetValue(period, m_context.Shift + shift);
    }

    //--------------------------------------------------
    // ATR Interface
    //--------------------------------------------------

    double GetATR(
        const int period,
        const int shift = 0)
    {
        return m_atrProvider.GetValue(period, m_context.Shift + shift);
    }

    bool GetATRValues(
        const int period,
        const int start_shift,
        const int count,
        double &values[])
    {
        return m_atrProvider.GetValues(
            period,
            m_context.Shift + start_shift,
            count,
            values);
    }

    //--------------------------------------------------
    // Reset
    //--------------------------------------------------

    void Reset()
    {
        m_emaProvider.Reset();
        m_atrProvider.Reset();
    }
};

#endif
