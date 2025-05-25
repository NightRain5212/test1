<template>
  <div class="chart-container" ref="chartContainer">
    <!-- 右上角控制按钮 -->
    <div class="control-panel">
      <button @click="resetView">
        <i class="icon-reset"></i> 重置视图
      </button>
      <button @click="toggle2D3D">
        <i class="icon-2d3d"></i> {{ is2D ? '3D模式' : '2D模式' }}
      </button>
    </div>
    
    <!-- ECharts容器 -->
    <div ref="chartEl" class="chart-3d"></div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts';
import 'echarts-gl';
import { ref, onMounted, onBeforeUnmount } from 'vue';

const chartEl = ref(null);
const chartContainer = ref(null);
let chartInstance = null;
const is2D = ref(false);

// 模拟数据
const mockData = () => {
  const data = [];
  for (let i = 0; i < 50; i++) {
    data.push([
      Math.random() * 100, // x
      Math.random() * 100, // y
      Math.random() * 100, // z
      Math.random() * 10   // 大小
    ]);
  }
  return data;
};

// 初始化图表
const initChart = () => {
  chartInstance = echarts.init(chartEl.value, 'dark');
  
  const option = {
    backgroundColor: '#1a1a1a',
    tooltip: {},
    visualMap: {
      show: false,
      dimension: 3,
      min: 0,
      max: 10,
      inRange: {
        size: [5, 20]
      }
    },
    xAxis3D: {
      type: 'value',
      name: 'X轴',
      axisLine: { lineStyle: { color: '#aaa' } }
    },
    yAxis3D: {
      type: 'value',
      name: 'Y轴',
      axisLine: { lineStyle: { color: '#aaa' } }
    },
    zAxis3D: {
      type: 'value',
      name: 'Z轴',
      axisLine: { lineStyle: { color: '#aaa' } }
    },
    grid3D: {
      viewControl: {
        autoRotate: false,
        rotateSensitivity: 1,  // 旋转灵敏度
        zoomSensitivity: 0.8,  // 缩放灵敏度
        distance: 150,         // 初始距离
        alpha: 40,             // 初始仰角
        beta: 30               // 初始旋转角
      },
      axisPointer: {
        lineStyle: { color: '#fff' }
      },
      light: {
        main: {
          intensity: 1.5,
          shadow: true,
          shadowQuality: 'high'
        },
        ambient: {
          intensity: 0.7
        }
      }
    },
    series: [{
      type: 'scatter3D',
      data: mockData(),
      symbolSize: 12,
      itemStyle: {
        color: function(params) {
          // 根据Z值渐变颜色
          const z = params.data[2];
          return `rgb(${Math.floor(z * 2.55)}, 100, 200)`;
        },
        opacity: 0.8
      },
      emphasis: {
        itemStyle: {
          color: '#ff0'
        }
      }
    }]
  };

  chartInstance.setOption(option);
  
  // 窗口大小变化时重绘
  window.addEventListener('resize', handleResize);
};

// 重置视图
const resetView = () => {
  chartInstance.setOption({
    grid3D: {
      viewControl: {
        alpha: 40,
        beta: 30,
        distance: 150
      }
    }
  });
};

// 切换2D/3D
const toggle2D3D = () => {
  is2D.value = !is2D.value;
  chartInstance.setOption({
    grid3D: {
      viewControl: {
        projection: is2D.value ? 'orthographic' : 'perspective'
      }
    }
  });
};

// 响应式调整
const handleResize = () => {
  chartInstance.resize();
};

onMounted(() => {
  initChart();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance.dispose();
});
</script>

<style scoped lang="scss">
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #1a1a1a;

  .chart-3d {
    width: 100%;
    height: 100%;
  }

  .control-panel {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 10;
    display: flex;
    gap: 10px;

    button {
      padding: 6px 12px;
      background: rgba(0, 0, 0, 0.7);
      color: #fff;
      border: 1px solid #444;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: rgba(50, 50, 50, 0.7);
      }

      i {
        display: inline-block;
        margin-right: 5px;
      }
    }
  }
}
</style>