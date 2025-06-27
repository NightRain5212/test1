<template>
  <div class="charts-container">
    <div class="charts">
      <div v-if="selectChart === 'radar-chart'" ref="radarChartContainer" style="width: 100%; height: 100%;"></div>
      <div v-else-if="selectChart === 'pie-chart'" ref="pieChartContainer" style="width: 100%; height: 100%;"></div>
      <div v-else-if="selectChart === 'bar-chart'" ref="barChartContainer" style="width: 100%; height: 100%;"></div>
     <div v-else-if="selectChart === 'histogram'" ref="HistogramContainer" style="width: 100%; height: 100%;"></div>
    <div v-else-if="selectChart === 'disk-chart'" ref="DiskContainer" style="width: 100%; height: 100%;"></div>
    </div>
    <div class="charts-menu">
      <n-menu v-model:value="selectChart" :options="chartsOptions" @update:value="handleChartChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch,nextTick } from 'vue';
import * as echarts from 'echarts';
import {
  PieChartOutline as PieIcon,
  SpeedometerOutline as RadarIcon,
  BarChartOutline as BarIcon,
  BarChartOutline as HistogramIcon,
  CopyOutline as DiskIcon,
} from "@vicons/ionicons5";

import { NIcon } from "naive-ui";
import { h } from "vue";

// 图表容器引用
const radarChartContainer = ref(null);
const pieChartContainer = ref(null);
const barChartContainer = ref(null);
const HistogramContainer = ref(null);
const DiskContainer = ref(null);
let radarChartInstance = null;
let pieChartInstance = null;
let barChartInstance = null;
let HistogramInstance = null;
let DiskInstance = null;
const selectChart = ref('radar-chart');

const level2Data = {
  '硬实力': [
    { value: 88, name: '专业知识' },
    { value: 67, name: '技术能力' },
    { value: 87, name: '经验积累' }
  ],
  '软实力': [
    { value: 55, name: '沟通能力' },
    { value: 54, name: '团队协作' },
    { value: 98, name: '表达能力' }
  ],
  '潜力': [
    { value: 35, name: '学习能力' },
    { value: 56, name: '创新能力' },
    { value: 97, name: '适应能力' }
  ],
  '文化水平': [
    { value: 35, name: '伦理抉择' },
    { value: 55, name: '价值观' }
  ],
  '外部指标': [
    { value: 50, name: '着装' },
    { value: 48, name: '行为举止' }
  ]
};
const weight1={
  '硬实力':'30%',
  '软实力':'30%',
  '潜力':'20%',
  '文化水平':'10%',
  '外部指标':'10%'
}
const weight2 = {
  '硬实力': [
    { name: '专业知识', weight: '35%' },
    { name: '技术能力', weight: '35%' },
    { name: '经验积累', weight: '30%' }
  ],
  '软实力': [
    { name: '沟通能力', weight: '35%' },
    { name: '团队协作', weight: '35%' },
    { name: '表达能力', weight: '30%' }
  ],
  '潜力': [
    { name: '学习能力', weight: '40%' },
    { name: '创新能力', weight: '35%' },
    { name: '适应能力', weight: '25%' }
  ],
  '文化水平': [
    { name: '伦理抉择', weight: '70%' },
    { name: '价值观', weight: '30%' }
  ],
  '外部指标': [
    { name: '着装', weight: '30%' },
    { name: '行为举止', weight: '70%' }
  ]
}
const level1Data = ['硬实力', '软实力', '潜力', '文化水平', '外部指标'].map(category => {
  const categoryData = level2Data[category] || [];
  const sum = categoryData.reduce((total, item) => {
    const weight = parseFloat(weight2[category].find(i => i.name === item.name).weight) / 100;  
    return total + (item.value * weight);
  }, 0);
  
  return {
    name: category,
    weight: weight1[category],
    value: sum
  };
});
const totalScore = ['硬实力', '软实力', '潜力', '文化水平', '外部指标'].reduce((sum, category) => {
  const categoryData = level2Data[category] || [];
  const categorySum = categoryData.reduce((catSum, item) => {
    const weight = parseFloat(weight2[category].find(i => i.name === item.name).weight) / 100;
    return catSum + (item.value * weight);
  }, 0);
  return sum + (categorySum * (parseFloat(weight1[category]) / 100));
}, 0);

// 菜单图标渲染:虚拟创建DOM
function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

// 菜单选项
const chartsOptions = [
  {
    label: "雷达图",
    key: "radar-chart",
    icon: renderIcon(RadarIcon)
  },
  {
    label: "饼图",
    key: "pie-chart",
    icon: renderIcon(PieIcon),
  },
  {
    label: "柱状图",
    key: "bar-chart",
    icon: renderIcon(BarIcon),
  },
  {
    label: "直方图",
    key: "histogram",
    icon: renderIcon(HistogramIcon),
  },
   {
    label: "磁盘图",
    key: "disk-chart",
    icon: renderIcon(DiskIcon),
  },
];
// 颜色配置
const level1Color = [
  '#ff4d4f', // 红色 - 硬实力
  '#ffa940', // 橙色 - 软实力
  '#ffec3d', // 黄色 - 潜力
  '#1890ff', // 蓝色 - 文化水平
  '#52c41a'  // 绿色 - 外部指标
];

const level2Color = {
  '硬实力': ['#ff7875', '#ff4d4f', '#f5222d'], // 红色系
  '软实力': ['#ffd591', '#ffa940', '#fa8c16'], // 橙色系
  '潜力': ['#fff566', '#ffec3d', '#fadb14'],   // 黄色系
  '文化水平': ['#69c0ff', '#1890ff', '#096dd9'], // 蓝色系
  '外部指标': ['#95de64', '#52c41a', '#389e0d']  // 绿色系
};
// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartContainer.value) return;
  if (radarChartInstance) { radarChartInstance.dispose(); }
  radarChartInstance = echarts.init(radarChartContainer.value, null, {
    renderer: 'canvas',
    useCoarsePointer: true,
    useDirtyRect: true,
    passive: true  // 启用被动事件监听
  });
  const option = {
    color: ['#67F9D8', '#FFE434', '#56A3F1', '#FF917C'],
    title: {
      text: '能力评估雷达图(总分:' + totalScore.toFixed(2) + '/100)',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item'// 这里的trigger属性设置为item，表示鼠标悬浮在数据点上时显示提示信息
    },
    legend: {
      data: ['评估结果'],
      bottom: 10
    },
    radar: {
      indicator: level1Data.map(item => ({
        text: item.name,
        max: 100
      })),
      center: ['50%', '50%'],//中心位置
      radius: '65%',//半径
      startAngle: 90,
      splitNumber: 4,
      shape: 'circle',
      axisName: {
        formatter: '【{value}】',
        color: '#428BD4'
      },
      splitArea: {
        areaStyle: {
          color: ['#77EADF', '#26C3BE', '#64AFE9', '#428BD4'],
          shadowColor: 'rgba(0, 0, 0, 0.2)',
          shadowBlur: 10//shadowBlur是模糊程度
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(211, 253, 250, 0.8)'
        }
      }
    },//设置雷达图的样式
    series: [{
      type: 'radar',
      data: [{
        value: level1Data.map(item => item.value),
        name: '评估结果',
        areaStyle: {
          color: 'rgba(103, 249, 216, 0.6)'
        },
        lineStyle: {
          width: 2,
          color: '#67F9D8'
        },
        symbol: 'circle',
        symbolSize: 6
      }],
      emphasis: {// 鼠标移入线条加粗
        lineStyle: {
          width: 4
        }
      }
    }]
  };
  radarChartInstance.setOption(option);
};

// 初始化饼图
const initPieChart = () => {
  if (!pieChartContainer.value) return;
  if (pieChartInstance) {
    pieChartInstance.dispose();
  }

  pieChartInstance = echarts.init(pieChartContainer.value, null, {
    renderer: 'canvas',
    useCoarsePointer: true,
    useDirtyRect: true,
    passive: true  // 启用被动事件监听
  });

  const option = {
    title: {
      text: '能力评估饼图(总分:' + totalScore.toFixed(2) + '/100)',
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const { name, value, percent } = params;
        const seriesName = params.seriesName;
        // 更丰富的提示框内容
        return `
          <div style="font-weight:bold">${seriesName}</div>
          <div>${name}</div>
          <div>分值: ${level2Data[seriesName].find(item => item.name === name).value}</div>
          <div>占比: ${percent}%</div>
        `;
      },
      backgroundColor: 'rgba(50,50,50,0.7)',
      borderColor: '#333',
      textStyle: {
        color: '#fff'
      },
      extraCssText: 'box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);'
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'middle',
      height: '70%',
      itemGap: 10,
      pageIconSize: 12,
      pageTextStyle: {
        color: '#666'
      },
      data: [
        ...level1Data.map(item => item.name),
        ...Object.values(level2Data).flat().map(item => item.name)
      ],
      formatter: (name) => {
        // 在图例中显示名称和值
        const allData = [...level1Data, ...Object.values(level2Data).flat()];
        const item = allData.find(d => d.name === name);
        return item ? `${name}: ${item.value}` : name;
      }
    },
    color: level1Color,
    grid: {
      top: 60,
      bottom: 20,
      left: 20,
      right: 150 // 为图例留出更多空间
    },
    series: [
      {
        name: '大类',
        type: 'pie',
        selectedMode: 'single',
        radius: [0, '40%'],
        center: ['40%', '50%'], // 调整中心位置
        label: {
          position: 'inner',
          fontSize: 14,
          formatter: '{b}\n{d}%'
        },
        labelLine: {
          show: false
        },
        data: level1Data.map((item, index) => {
          // 计算该大类下所有子类的原始值总和
          const originalTotal = level2Data[item.name]?.reduce((sum, subItem) => sum + subItem.value, 0) || 0;

          // 获取该大类的权重
          const categoryWeight = weight1[item.name] || '0%';

          return {
            ...item,
            itemStyle: {
              color: level1Color[index]
            },
            tooltip: {
              formatter: [
                `<div style="font-weight:bold">${item.name}</div>`,
                `<div>权重: ${categoryWeight}</div>`,
                `<div>原始总分: ${originalTotal.toFixed(2)}</div>`,
                `<div>加权值: ${item.value.toFixed(2)}</div>`,
                `<div>占比: {d}%</div>`
              ].join('')
            }
          }
        })
      },
      {
        name: '细分',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'], // 与一级饼图保持一致
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%',
          fontSize: 12
        },
        labelLine: {
          length: 10,
          length2: 15,
          smooth: true
        },
        emphasis: {
          scale: true,
          scaleSize: 10,
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          },
          label: {
            show: true,
            fontWeight: 'bold'
          }
        },
        data: level1Data.flatMap(parentItem => {
          const children = level2Data[parentItem.name] || [];
          const colors = level2Color[parentItem.name] || [];
          const subWeights = weight2[parentItem.name] || []; // 获取当前大类的子类权重

          return children.map((child, childIndex) => {
            // 找到当前子类对应的权重
            const subWeight = subWeights.find(item => item.name === child.name)?.weight || '0%';
            const weightedValue = child.value * (parseFloat(subWeight) / 100);

            return {
              ...child,
              value: weightedValue, // 使用加权后的值
              originalValue: child.value, // 保留原始值（可选）
              itemStyle: {
                color: colors[Math.floor(childIndex * colors.length / children.length)] || colors[0]
              },
              tooltip: {
                formatter: `${child.name}<br/>原始分值: ${child.value}<br/>加权分值: ${weightedValue.toFixed(2)}<br/>权重: ${subWeight}<br/>占比: {d}%`
              }
            };
          });
        })
      }
    ]
  };

  pieChartInstance.setOption(option);

  // 添加窗口大小变化时的自适应
  window.addEventListener('resize', function () {
    pieChartInstance.resize();
  });
};
// 初始化柱状图
const initBarChart = () => {
  if (!barChartContainer.value) return;
  barChartInstance?.dispose();

  barChartInstance = echarts.init(barChartContainer.value, null, {
    renderer: 'canvas',
    useCoarsePointer: true,
    useDirtyRect: true,
    passive: true  // 启用被动事件监听
  });

  // 1. 重构数据结构为二维表
  const datasetSource = [['category']];
  const subCategories = new Set(); // 收集所有子类名称

  // 添加列名（子类名称）
  Object.values(level2Data).forEach(items => {
    items.forEach(item => subCategories.add(item.name));
  });
  datasetSource[0].push(...subCategories);
  datasetSource[0].push('weight'); // 最后一列存储大类权重

  // 填充数据行
  level1Data.forEach(mainItem => {
    const row = [mainItem.name];
    const subItems = level2Data[mainItem.name] || [];

    // 填充每个子类的加权值
    subCategories.forEach(subName => {
      const subItem = subItems.find(item => item.name === subName);
      if (subItem) {
        const weight = parseFloat(weight2[mainItem.name].find(w => w.name === subName).weight) / 100;
        row.push(subItem.value * weight);
      } else {
        row.push(0); // 无此子类填0
      }
    });

    row.push(parseFloat(mainItem.weight)); // 添加大类权重
    datasetSource.push(row);
  });

  // 2. 动态生成series配置
  const series = Array.from(subCategories).map((subName, idx) => ({
    name: subName,
    type: 'bar',
    stack: 'total', // 所有系列堆叠到同一组
    encode: {
      x: 'category',
      y: subName,
      itemName: 'category', // 用于tooltip
    },
    barWidth: '50%',
    itemStyle: {
      color: (params) => {
        // 1. 找到当前大类
        const mainCat = level1Data.find(cat =>
          level2Data[cat.name]?.some(item => item.name === subName));

        // 2. 获取该大类下的子类数组
        const subItems = level2Data[mainCat?.name] || [];

        // 3. 找到当前子类在该大类中的索引
        const subIndex = subItems.findIndex(item => item.name === subName);

        // 4. 返回对应颜色
        return level2Color[mainCat?.name]?.[subIndex] || '#999';
      },
      borderRadius: [4, 4, 0, 0],
      borderColor: '#fff',
      borderWidth: 1
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }));

  // 3. 完整配置
  const option = {
    dataset: { source: datasetSource },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const mainItem = level1Data.find(item => item.name === params.name);
        const subItem = level2Data[params.name]?.find(item => item.name === params.seriesName);
        const weightObj = weight2[params.name]?.find(w => w.name === params.seriesName);

        if (!subItem || !weightObj) return '';

        const weightedValue = subItem.value * (parseFloat(weightObj.weight) / 100);

        return `
          <div style="font-weight:bold;margin-bottom:5px">${params.name} · ${params.seriesName}</div>
          <div style="display:flex;justify-content:space-between">
            <span>原始值:</span>
            <span>${subItem.value}</span>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span>权重:</span>
            <span>${weightObj.weight}</span>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span>加权值:</span>
            <span>${weightedValue.toFixed(2)}</span>
          </div>
          <div style="display:flex;justify-content:space-between">
            <span>大类权重:</span>
            <span>${mainItem.weight}</span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:5px">
            <span>大类总分:</span>
            <span>${mainItem.value.toFixed(2)}</span>
          </div>
        `;
      },
      backgroundColor: 'rgba(50,50,50,0.9)',
      borderWidth: 0,
      padding: 10,
      textStyle: { color: '#fff' }
    },
    title: {
      text: '能力评估柱状图(总分:' + totalScore.toFixed(2) + '/100)',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    legend: {
      data: Array.from(subCategories),
      bottom: 5,
      itemGap: 10,
      textStyle: { fontSize: 12 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '20%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      axisLabel: {
        interval: 0,
        rotate: 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { fontSize: 12 }
    },
    series
  };

  barChartInstance.setOption(option);
  window.addEventListener('resize', () => barChartInstance.resize());
};
//初始化直方图
const initHistogram = () => {
  if (!HistogramContainer.value) return;
  HistogramInstance?.dispose();

  HistogramInstance = echarts.init(HistogramContainer.value, null, {
    renderer: 'canvas',
    useCoarsePointer: true,
    useDirtyRect: true,
    passive: true  // 启用被动事件监听
  });

  // 准备数据：将层级数据转换为直方图需要的格式
  const data = [];
  let currentX = 0; // 当前x轴位置

  level1Data.forEach(mainItem => {
    const subItems = level2Data[mainItem.name] || [];
    const mainWeight = parseFloat(mainItem.weight) / 100; // 大类权重系数

    subItems.forEach((subItem, subIndex) => {
      const subWeight = parseFloat(weight2[mainItem.name].find(w => w.name === subItem.name).weight) / 100;
      const width = mainWeight * subWeight; // 宽度 = 大类权重 × 小类权重

      data.push({
        value: [
          currentX, // 起始位置
          currentX + width * 100, // 结束位置（乘以100放大显示效果）
          subItem.value, // 高度值
          `${mainItem.name}|${subItem.name}` // 组合名称
        ],
        itemStyle: {
          color: level2Color[mainItem.name]?.[subIndex] || '#999'
        }
      });

      currentX += width * 100; // 更新x轴位置
    });
  });

  const option = {
    title: {
      text: '能力评估直方图(总分:' + totalScore.toFixed(2) + '/100)',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: params => {
        const [mainName, subName] = params.name.split('|');
        const subItem = level2Data[mainName]?.find(item => item.name === subName);
        const weightObj = weight2[mainName]?.find(w => w.name === subName);
        const mainWeight = weight1[mainName] || '0%';
        return `
          <div style="font-weight:bold">${mainName} · ${subName}</div>
          <div>原始值: ${subItem?.value || 0}</div>
          <div>${mainName}权重:${mainWeight}|| '0%'</div>
          <div>权重: ${weightObj?.weight || '0%'}</div>
          <div>加权值: ${params.value[2].toFixed(2)}</div>
        `;
      }
    },
    xAxis: {
      type: 'value',
      scale: true,
      axisLabel: { show: false } // 隐藏x轴标签
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'custom',
      renderItem: (params, api) => {
        const yValue = api.value(2);
        const start = api.coord([api.value(0), yValue]);
        const size = api.size([api.value(1) - api.value(0), yValue]);
        const style = api.style();

        return {
          type: 'rect',
          shape: {
            x: start[0],
            y: start[1],
            width: size[0],
            height: size[1]
          },
          style: style
        };
      },
      dimensions: ['from', 'to', 'value', 'name'],
      encode: {
        x: [0, 1],
        y: 2,
        itemName: 3
      },
      data: data,
      label: {
        show: true,
        position: 'top',
        formatter: params => params.value[3].split('|')[1] // 显示子类名称
      }
    }]
  };

  HistogramInstance.setOption(option);
  window.addEventListener('resize', () => HistogramInstance.resize());
};
//初始化磁盘图
const initDiskChart = () => {
  if (!DiskContainer.value) return;
  DiskInstance?.dispose();

  DiskInstance = echarts.init(DiskContainer.value, null, {
    renderer: 'canvas',
    useCoarsePointer: true,
    useDirtyRect: true,
    passive: true  // 启用被动事件监听
  });

  const treemapData = level1Data.map((mainItem, mainIndex) => {
    const children = level2Data[mainItem.name].map((subItem, subIndex) => {
      const weightObj = weight2[mainItem.name].find(w => w.name === subItem.name);
      const weightedValue = subItem.value * (parseFloat(weightObj.weight) / 100);

      return {
        name: subItem.name,
        value: weightedValue,
        rawValue: subItem.value,
        weight: weightObj.weight,
        itemStyle: {
          color: level2Color[mainItem.name][subIndex % level2Color[mainItem.name].length]
        }
      };
    });

    return {
      name: mainItem.name,
      value: mainItem.value,
      weight: mainItem.weight,
      itemStyle: {
        color: level1Color[mainIndex],
        borderWidth: 0 // Remove border for main categories
      },
      children: children
    };
  });

  const option = {
    title: {
      text: '能力评估磁盘图(总分:' + totalScore.toFixed(2) + '/100)',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      formatter: function (info) {
        const treePathInfo = info.treePathInfo;
        const isMainCategory = treePathInfo.length === 1;

        if (isMainCategory) {
          const mainItem = info.data;
          // Calculate sum of raw values for this category
          const rawSum = level2Data[mainItem.name].reduce((sum, item) => sum + item.value, 0);
          return `
            <div style="font-weight:bold;margin-bottom:5px">${mainItem.name}</div>
            <div>${mainItem.name}权重: ${mainItem.weight}</div>
            <div>原始值总和: ${rawSum}</div>
            <div>加权总和: ${mainItem.value.toFixed(2)}</div>
            <div style="margin-top:5px;color:#666">点击查看细分项</div>
          `;
        } else {
          const mainName = treePathInfo[1].name;
          const subItem = info.data;
          const mainWeight = weight1[mainName];
          // 获取当前大类的加权总和（mainValue）
          const mainValue = level1Data.find(item => item.name === mainName)?.value.toFixed(2) || '0';

          return `
    <div style="font-weight:bold">${mainName} · ${subItem.name}</div>
    <div>权重: ${mainWeight} · ${subItem.weight}</div>
    <div>原始值: ${subItem.rawValue}</div>
    <div>加权值: ${subItem.value.toFixed(2)}/${mainValue}</div>
    <div>综合值: ${(subItem.value * parseFloat(mainWeight) / 100).toFixed(2)}/${(mainValue * parseFloat(mainWeight) / 100).toFixed(2)}</div>
  `;
        }
      }
    },
    series: [{
      name: '能力评估',
      type: 'treemap',
      visibleMin: 10,
      label: {
        show: true,
        formatter: function (params) {
          // Only show labels for level2 items
          return params.treePathInfo.length > 1 ? params.name : '';
        }
      },
      upperLabel: {
        show: false // Disable upper labels completely
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1
      },
      levels: [
        {
          // Level 1 style (main categories)
          itemStyle: {
            borderWidth: 0,
            gapWidth: 0 // Remove gaps between main categories
          },
          label: {
            show: false // Hide labels for level1
          }
        },
        {
          // Level 2 style (sub categories)
          itemStyle: {
            borderWidth: 1,
            gapWidth: 1
          }
        }
      ],
      data: treemapData
    }]
  };

  DiskInstance.setOption(option);
};
// 切换图表时的清理
const handleChartChange = (key) => {
  if (selectChart.value === 'radar-chart') {
    if(radarChartInstance&&!radarChartInstance.isDisposed){
      radarChartInstance.dispose()
    }
  } else if(selectChart.value === 'pie-chart'){
    if(pieChartInstance&&!pieChartInstance.isDisposed){
      pieChartInstance.dispose()
    }
  }else if(selectChart.value === 'bar-chart'){
    if(barChartInstance&&!barChartInstance.isDisposed){
      barChartInstance.dispose()
    }
  }
  else if(selectChart.value === 'histogram'){
    if(HistogramInstance&&!HistogramInstance.isDisposed){
      HistogramInstance.dispose()
    }
  }  else if(selectChart.value === 'disk-chart'){
    if(DiskInstance&&!DiskInstance.isDisposed){
      DiskInstance.dispose()
    }
  }
  selectChart.value = key
  nextTick(() => {
    if (key === 'radar-chart') {
      initRadarChart()
    } else if(key === 'pie-chart'){
      initPieChart()
    }else if(key === 'bar-chart'){
      initBarChart()
    }else if(key === 'histogram'){
      initHistogram()
    }else if(key === 'disk-chart'){
      initDiskChart()
    }
  })
} 

// 响应式调整
const handleResize = () => {
  if (radarChartInstance) radarChartInstance.resize();
  if (pieChartInstance) pieChartInstance.resize();
  if (barChartInstance) barChartInstance.resize();
  if (HistogramInstance) HistogramInstance.resize();
   if (DiskInstance) DiskInstance.resize();
};

onMounted(() => {
  initRadarChart();
  window.addEventListener('resize', handleResize);
});

// 组件卸载前的清理
onBeforeUnmount(() => {
  if (radarChartInstance) {
    radarChartInstance.dispose()
  }
  if (pieChartInstance) {
    pieChartInstance.dispose()
  }
  if (barChartInstance) {
    barChartInstance.dispose()
  }
    if (HistogramInstance) {
    HistogramInstance.dispose()
  }
      if (DiskInstance) {
    DiskInstance.dispose()
  }
  // 同时移除窗口resize监听器
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.charts-container {
  display: flex;
  width: 100%;
  height: 600px;
}

.charts {
  width: 80%;
  height: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px;
}

.charts-menu {
  width: 20%;
  padding-left: 5px;
  background-color: rgb(255, 255, 255);
}
</style>