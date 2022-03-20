<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="1" simplifyDrawingTol="1" simplifyMaxScale="1" simplifyAlgorithm="0" version="3.16.0-Hannover" minScale="100000000" labelsEnabled="0" maxScale="0" simplifyLocal="1" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal fixedDuration="0" enabled="0" startField="begin" durationUnit="min" endField="end" endExpression="" mode="2" startExpression="" accumulate="0" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="singleSymbol" symbollevels="0" enableorderby="0" forceraster="0">
    <symbols>
      <symbol type="fill" force_rhr="0" clip_to_extent="1" name="0" alpha="1">
        <layer pass="0" enabled="1" class="SimpleFill" locked="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="152,125,183,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory penWidth="0" diagramOrientation="Up" rotationOffset="270" spacingUnit="MM" sizeScale="3x:0,0,0,0,0,0" opacity="1" spacingUnitScale="3x:0,0,0,0,0,0" showAxis="1" labelPlacementMethod="XHeight" penColor="#000000" maxScaleDenominator="1e+08" enabled="0" spacing="5" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" minScaleDenominator="0" minimumSize="0" scaleDependency="Area" lineSizeType="MM" height="15" scaleBasedVisibility="0" direction="0" width="15" backgroundColor="#ffffff" sizeType="MM" backgroundAlpha="255" barWidth="5">
      <fontProperties style="" description=".AppleSystemUIFont,13,-1,5,50,0,0,0,0,0"/>
      <axisSymbol>
        <symbol type="line" force_rhr="0" clip_to_extent="1" name="" alpha="1">
          <layer pass="0" enabled="1" class="SimpleLine" locked="0">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings priority="0" placement="1" dist="0" zIndex="0" obstacle="0" linePlacementFlags="18" showAll="1">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option type="Map" name="QgsGeometryGapCheck">
        <Option type="double" value="0" name="allowedGapsBuffer"/>
        <Option type="bool" value="false" name="allowedGapsEnabled"/>
        <Option type="QString" value="" name="allowedGapsLayer"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="fid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="Name" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="description" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="timestamp" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="begin" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="end" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="altitudeMode" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="tessellate" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="extrude" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="visibility" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="drawOrder" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="icon" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="fid" name=""/>
    <alias index="1" field="Name" name=""/>
    <alias index="2" field="description" name=""/>
    <alias index="3" field="timestamp" name=""/>
    <alias index="4" field="begin" name=""/>
    <alias index="5" field="end" name=""/>
    <alias index="6" field="altitudeMode" name=""/>
    <alias index="7" field="tessellate" name=""/>
    <alias index="8" field="extrude" name=""/>
    <alias index="9" field="visibility" name=""/>
    <alias index="10" field="drawOrder" name=""/>
    <alias index="11" field="icon" name=""/>
  </aliases>
  <defaults>
    <default field="fid" expression="" applyOnUpdate="0"/>
    <default field="Name" expression="" applyOnUpdate="0"/>
    <default field="description" expression="" applyOnUpdate="0"/>
    <default field="timestamp" expression="" applyOnUpdate="0"/>
    <default field="begin" expression="" applyOnUpdate="0"/>
    <default field="end" expression="" applyOnUpdate="0"/>
    <default field="altitudeMode" expression="" applyOnUpdate="0"/>
    <default field="tessellate" expression="" applyOnUpdate="0"/>
    <default field="extrude" expression="" applyOnUpdate="0"/>
    <default field="visibility" expression="" applyOnUpdate="0"/>
    <default field="drawOrder" expression="" applyOnUpdate="0"/>
    <default field="icon" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" notnull_strength="1" field="fid" constraints="3" unique_strength="1"/>
    <constraint exp_strength="0" notnull_strength="0" field="Name" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="description" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="timestamp" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="begin" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="end" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="altitudeMode" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="tessellate" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="extrude" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="visibility" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="drawOrder" constraints="0" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" field="icon" constraints="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="fid" exp=""/>
    <constraint desc="" field="Name" exp=""/>
    <constraint desc="" field="description" exp=""/>
    <constraint desc="" field="timestamp" exp=""/>
    <constraint desc="" field="begin" exp=""/>
    <constraint desc="" field="end" exp=""/>
    <constraint desc="" field="altitudeMode" exp=""/>
    <constraint desc="" field="tessellate" exp=""/>
    <constraint desc="" field="extrude" exp=""/>
    <constraint desc="" field="visibility" exp=""/>
    <constraint desc="" field="drawOrder" exp=""/>
    <constraint desc="" field="icon" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column type="field" width="-1" name="fid" hidden="0"/>
      <column type="field" width="-1" name="Name" hidden="0"/>
      <column type="field" width="-1" name="description" hidden="0"/>
      <column type="field" width="-1" name="timestamp" hidden="0"/>
      <column type="field" width="-1" name="begin" hidden="0"/>
      <column type="field" width="-1" name="end" hidden="0"/>
      <column type="field" width="-1" name="altitudeMode" hidden="0"/>
      <column type="field" width="-1" name="tessellate" hidden="0"/>
      <column type="field" width="-1" name="extrude" hidden="0"/>
      <column type="field" width="-1" name="visibility" hidden="0"/>
      <column type="field" width="-1" name="drawOrder" hidden="0"/>
      <column type="field" width="-1" name="icon" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="Name" editable="1"/>
    <field name="altitudeMode" editable="1"/>
    <field name="begin" editable="1"/>
    <field name="description" editable="1"/>
    <field name="drawOrder" editable="1"/>
    <field name="end" editable="1"/>
    <field name="extrude" editable="1"/>
    <field name="fid" editable="1"/>
    <field name="icon" editable="1"/>
    <field name="tessellate" editable="1"/>
    <field name="timestamp" editable="1"/>
    <field name="visibility" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="Name"/>
    <field labelOnTop="0" name="altitudeMode"/>
    <field labelOnTop="0" name="begin"/>
    <field labelOnTop="0" name="description"/>
    <field labelOnTop="0" name="drawOrder"/>
    <field labelOnTop="0" name="end"/>
    <field labelOnTop="0" name="extrude"/>
    <field labelOnTop="0" name="fid"/>
    <field labelOnTop="0" name="icon"/>
    <field labelOnTop="0" name="tessellate"/>
    <field labelOnTop="0" name="timestamp"/>
    <field labelOnTop="0" name="visibility"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"Name"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
