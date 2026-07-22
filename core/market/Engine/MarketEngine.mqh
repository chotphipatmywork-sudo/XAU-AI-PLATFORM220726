//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketEngine.mqh                                       |
//| Layer   : Market / Engine                                        |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_ENGINE_MARKETENGINE_MQH
#define CORE_MARKET_ENGINE_MARKETENGINE_MQH

#include "../models/MarketContext.mqh"
#include "../models/PriceSeries.mqh"

#include "../models/SwingPoint.mqh"
#include "../models/StructureState.mqh"

#include "../detectors/SwingDetector.mqh"
#include "../detectors/StructureDetector.mqh"
#include "../detectors/BOSDetector.mqh"

class CMarketEngine
{
private:

    CSwingDetector      m_swingDetector;
    CStructureDetector  m_structureDetector;
    CBOSDetector        m_bosDetector;

    CSwingPoint         m_previousSwing;
    CSwingPoint         m_currentSwing;

public:

    CMarketEngine()
    {
        m_previousSwing.Reset();
        m_currentSwing.Reset();
    }

    bool Analyze(
        CPriceSeriesModel &series,
        CMarketContext &context)
    {
        //--------------------------------------------------
        // Swing
        //--------------------------------------------------

        if(!m_swingDetector.FindLastSwing(
                series,
                m_currentSwing))
        {
            return false;
        }

        //--------------------------------------------------
        // Structure
        //--------------------------------------------------

        CStructureState structure;
        structure.Reset();

        if(!m_structureDetector.Detect(
                m_previousSwing,
                m_currentSwing,
                structure))
        {
            return false;
        }

        //--------------------------------------------------
        // BOS
        //--------------------------------------------------

        CBOSState bos;
        bos.Reset();

        m_bosDetector.Detect(
            structure,
            bos);

        //--------------------------------------------------
        // Context
        //--------------------------------------------------

        context.StructureState = structure.Trend;

        //--------------------------------------------------
        // Save
        //--------------------------------------------------

        m_previousSwing = m_currentSwing;

        return true;
    }

};

#endif