//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainOrchestrator.mqh                                  |
//| Layer   : Engine                                                 |
//| Version : 2.0.0                                                  |
//| Purpose : Brain Orchestrator                                     |
//+------------------------------------------------------------------+

#ifndef CORE_ENGINE_BRAINORCHESTRATOR_MQH
#define CORE_ENGINE_BRAINORCHESTRATOR_MQH

#include "../brain/Brain.mqh"

#include "BrainWorkspace.mqh"

#include "models/BrainPipelineResult.mqh"

//--------------------------------------------------
// Brain Orchestrator
//--------------------------------------------------

class CBrainOrchestrator
{
private:

    CBrain m_brain;

public:

    //--------------------------------------------------

    bool Initialize()
    {
        return m_brain.Initialize();
    }

    //--------------------------------------------------

    CBrainPipelineResult Execute(
        const string symbol,
        ENUM_TIMEFRAMES timeframe)
    {
        CBrainWorkspace workspace;

        workspace.Reset();

        workspace.Symbol = symbol;
        workspace.Timeframe = timeframe;

        //--------------------------------------------------
        // Brain
        //--------------------------------------------------

        workspace.Result =
            m_brain.Think(
                workspace.Symbol,
                workspace.Timeframe);

        return workspace.Result;
    }

    //--------------------------------------------------

    void Shutdown()
    {
        m_brain.Shutdown();
    }
};

#endif